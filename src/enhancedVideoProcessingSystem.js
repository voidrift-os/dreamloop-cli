const RateLimiter = require('./rateLimiter');
const { EnhancedEventBus } = require('./eventBus');
const HealthCheckService = require('./healthCheckService');
const ConfigManager = require('./configManager');
const WorkflowBuilder = require('./workflowBuilder');
const logger = require('./logger');

class VideoProcessingSystem {}

class EnhancedVideoProcessingSystem extends VideoProcessingSystem {
  constructor() {
    super();
    this.eventBus = new EnhancedEventBus();
    this.configManager = new ConfigManager();
    this.rateLimiter = new RateLimiter(
      this.configManager.get('rate.limit.requests'),
      this.configManager.get('rate.limit.window')
    );
    this.cache = {};
    this.circuitBreaker = { state: 'CLOSED', failureCount: 0 };
    this.healthCheck = new HealthCheckService({
      eventBus: this.eventBus,
      cache: this.cache,
      circuitBreaker: this.circuitBreaker
    });
    this.workflowBuilder = new WorkflowBuilder(this.eventBus);
    this.logger = logger;
    this.metrics = { increment: () => {} };
    this.orchestrator = { generateVideoId: () => `video_${Date.now()}` };
    this.videoStatusStore = new Map(); // TODO: replace with persistent store

    this.createCustomWorkflows();
    this.setupMonitoring();
  }

  createCustomWorkflows() {
    const builder = this.workflowBuilder.createWorkflow('high_priority_video');
    builder
      .addStep('validate_input', async (ctx) => {
        if (!ctx.promptParams.topic) throw new Error('Topic is required');
        return { validated: true };
      })
      .addStep('generate_content', async (ctx) => {
        return this.generateContentWithPriority(ctx.promptParams);
      }, { timeout: 60000 })
      .addStep('create_video', async (ctx) => {
        const content = ctx.results.get('generate_content');
        const video = await this.createVideoWithPriority(content.prompt);
        this.videoStatusStore.set(video.videoId, { status: 'processing', createdAt: Date.now() });
        return video;
      }, { timeout: 120000, compensate: async () => logger.info('Cleaning up resources') })
      .build();
  }

  setupMonitoring() {
    this.eventBus.subscribe('message.dead_letter', ({ data }) => {
      const { message } = data;
      this.logger.error('Message to dead letter', { id: message.id, type: message.type });
      this.metrics.increment('dead_letter_queue.messages');
    });
    this.eventBus.subscribe('health.check.completed', ({ data }) => {
      const { status } = data;
      this.metrics.increment('health_check.completed', { status });
      if (status === 'unhealthy') {
        this.logger.warn('System health check failed');
      }
    });
    this.configManager.watch('*', (key, value, oldValue) => {
      this.logger.info('Configuration changed', { key, value, oldValue });
    });
  }

  async processVideo(promptParams, options = {}) {
    const userId = options.userId || 'anonymous';
    const priority = options.priority || 'normal';
    this.rateLimiter.checkLimit(userId);
    const correlationId = this.eventBus.generateId();
    this.logger.info('Processing video request', { correlationId, userId, priority });
    if (priority === 'high') {
      const result = await this.workflowBuilder.executeWorkflow('high_priority_video', { promptParams, correlationId, userId });
      const videoId = result.create_video?.videoId;
      if (videoId) this.videoStatusStore.set(videoId, { status: 'completed', updatedAt: Date.now() });
      return { correlationId, workflowResult: result };
    }
    this.eventBus.emit('workflow.start', { videoId: this.orchestrator.generateVideoId(), promptParams, correlationId, userId });
    return { correlationId };
  }

  async generateContentWithPriority(promptParams) {
    return { prompt: `High-priority: ${JSON.stringify(promptParams)}` };
  }

  async createVideoWithPriority(prompt) {
    return { videoId: `priority_${Date.now()}`, status: 'created' };
  }

  getSystemHealth() { return this.healthCheck.getHealthStatus(); }

  getConfiguration() { return this.configManager.getAll(true); }

  updateConfiguration(key, value) { this.configManager.set(key, value); }

  getDeadLetterMessages() { return this.eventBus.getDeadLetterMessages(); }

  reprocessDeadLetter(id) { return this.eventBus.reprocessDeadLetter(id); }

  getRateLimitStatus(userId) {
    return { requests: this.rateLimiter.requests.get(userId) || [], limit: this.rateLimiter.maxRequests, window: this.rateLimiter.windowMs };
  }

  getVideoStatus(id) { return this.videoStatusStore.get(id) || null; }
}

module.exports = EnhancedVideoProcessingSystem;

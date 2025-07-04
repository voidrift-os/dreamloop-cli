const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const Joi = require('joi');
const logger = require('./logger');
const EnhancedVideoProcessingSystem = require('./enhancedVideoProcessingSystem');

const API_KEY = process.env.API_KEY;
if (!API_KEY || API_KEY === 'my-super-secret-key') {
  throw new Error('Missing or insecure API_KEY environment variable');
}

const app = express();
const system = new EnhancedVideoProcessingSystem();

app.use(cors());
app.use(bodyParser.json());

// API key middleware
app.use((req, res, next) => {
  if (req.headers['x-api-key'] !== API_KEY) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  next();
});

// Rate limiter middleware for /config POST
app.post('/config', (req, res, next) => {
  try {
    system.rateLimiter.checkLimit(req.ip);
    next();
  } catch (err) {
    res.status(429).json({ error: 'Rate limit exceeded' });
  }
});

// Validation schemas
const configSchema = Joi.object({ key: Joi.string().required(), value: Joi.any() });
const processSchema = Joi.object({
  promptParams: Joi.object().required(),
  options: Joi.object().optional()
});

// Routes
app.get('/system-health', (req, res) => {
  res.json(system.getSystemHealth());
});

app.get('/rate-limit/:userId', (req, res) => {
  res.json(system.getRateLimitStatus(req.params.userId));
});

app.get('/config', (req, res) => {
  res.json(system.getConfiguration());
});

const nonSensitiveRegex = /^(?!.*(apiKey|credentialId|voiceId)).*/i;

app.post('/config', (req, res) => {
  const { error, value } = configSchema.validate(req.body);
  if (error) return res.status(400).json({ error: error.message });
  if (!nonSensitiveRegex.test(value.key)) {
    return res.status(400).json({ error: 'Cannot update sensitive keys' });
  }
  system.updateConfiguration(value.key, value.value);
  res.json({ success: true, config: system.getConfiguration() });
});

app.get('/dead-letter', (req, res) => {
  res.json(system.getDeadLetterMessages());
});

app.post('/reprocess-dead-letter', (req, res) => {
  const { messageId } = req.body || {};
  const ok = system.reprocessDeadLetter(messageId);
  res.json({ success: ok });
});

app.post('/process-video', (req, res) => {
  const { error, value } = processSchema.validate(req.body);
  if (error) return res.status(400).json({ error: error.message });
  system.processVideo(value.promptParams, value.options || {})
    .then(result => res.json(result))
    .catch(err => {
      logger.error('Process video failed', { error: err.message });
      res.status(500).json({ error: err.message });
    });
});

app.get('/video-status/:videoId', async (req, res) => {
  const status = await system.getVideoStatus(req.params.videoId);
  if (!status) return res.status(404).json({ error: 'Video not found' });
  res.json({ videoId: req.params.videoId, status });
});

app.get('/', (req, res) => {
  res.json({ message: 'Dreamloop Enhanced Video System API' });
});

const PORT = process.env.PORT || 9001;
app.listen(PORT, () => {
  logger.info(`Server running at http://localhost:${PORT}`);
});

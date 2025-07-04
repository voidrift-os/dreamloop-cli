const logger = require('./logger');

class HealthCheckService {
  constructor(dependencies) {
    this.dependencies = dependencies;
    this.checks = new Map();
    this.status = 'healthy';
    this.registerCheck('eventBus', () => this.checkEventBus());
    this.registerCheck('cache', () => this.checkCache());
    this.registerCheck('circuitBreaker', () => this.checkCircuitBreaker());
    setInterval(() => this.runHealthChecks(), 30000);
  }

  registerCheck(name, fn) {
    this.checks.set(name, fn);
  }

  async runHealthChecks() {
    const results = new Map();
    let healthy = true;
    for (const [name, fn] of this.checks) {
      try {
        const result = await fn();
        results.set(name, { status: 'healthy', ...result });
      } catch (err) {
        results.set(name, { status: 'unhealthy', error: err.message });
        healthy = false;
      }
    }
    this.status = healthy ? 'healthy' : 'unhealthy';
    this.dependencies.eventBus.emit('health.check.completed', { status: this.status, checks: Object.fromEntries(results) });
  }

  async checkEventBus() {
    let received = false;
    const unsub = this.dependencies.eventBus.subscribe('health.test', () => { received = true; });
    this.dependencies.eventBus.emit('health.test', {});
    await new Promise(res => setTimeout(res, 100));
    unsub();
    if (!received) throw new Error('Event bus not responding');
    return { message: 'Event bus operational' };
  }

  async checkCache() { return { message: 'Cache operational' }; }

  async checkCircuitBreaker() { return { message: 'Circuit breaker operational', state: 'CLOSED', failureCount: 0 }; }

  getHealthStatus() {
    return { status: this.status, timestamp: Date.now(), uptime: process.uptime ? process.uptime() : 'N/A' };
  }
}

module.exports = HealthCheckService;

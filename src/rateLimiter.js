class RateLimiter {
  constructor(maxRequests = 100, windowMs = 60000, cleanupIntervalMs = 10000, maxKeys = 1000) {
    this.maxRequests = maxRequests;
    this.windowMs = windowMs;
    this.cleanupIntervalMs = cleanupIntervalMs;
    this.maxKeys = maxKeys;
    this.requests = new Map();
    setInterval(() => this.cleanup(), this.cleanupIntervalMs);
  }

  checkLimit(key) {
    const now = Date.now();
    let userRequests = this.requests.get(key) || [];
    userRequests = userRequests.filter(t => now - t < this.windowMs);
    if (userRequests.length >= this.maxRequests) {
      throw new Error(`Rate limit exceeded for ${key}`);
    }
    userRequests.push(now);
    if (!this.requests.has(key) && this.requests.size >= this.maxKeys) {
      const oldestKey = this.requests.keys().next().value;
      this.requests.delete(oldestKey);
    }
    this.requests.set(key, userRequests);
  }

  cleanup() {
    const now = Date.now();
    for (const [key, requests] of this.requests) {
      const valid = requests.filter(t => now - t < this.windowMs);
      if (valid.length === 0) {
        this.requests.delete(key);
      } else {
        this.requests.set(key, valid);
      }
    }
  }
}

module.exports = RateLimiter;

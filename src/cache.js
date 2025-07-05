const client = require('./redisClient');

class Cache {
  constructor(defaultTtl = 3600) {
    this.defaultTtl = defaultTtl;
    this.memory = new Map();
  }

  async get(key) {
    if (client && client.isOpen) {
      const val = await client.get(key);
      return val ? JSON.parse(val) : null;
    }
    const entry = this.memory.get(key);
    if (!entry) return null;
    if (Date.now() > entry.exp) {
      this.memory.delete(key);
      return null;
    }
    return entry.value;
  }

  async set(key, value, ttl = this.defaultTtl) {
    if (client && client.isOpen) {
      await client.set(key, JSON.stringify(value), { EX: ttl });
      return;
    }
    this.memory.set(key, { value, exp: Date.now() + ttl * 1000 });
  }

  async del(key) {
    if (client && client.isOpen) {
      await client.del(key);
      return;
    }
    this.memory.delete(key);
  }
}

module.exports = new Cache();

const logger = require('./logger');
let client;

try {
  const { createClient } = require('redis');
  const url = process.env.REDIS_URL || 'redis://localhost:6379';
  client = createClient({ url });
  client.on('error', err => logger.error('Redis client error', { error: err.message }));
  client.connect().catch(err => logger.error('Redis connect error', { error: err.message }));
} catch (err) {
  logger.warn('Redis module not available, using in-memory stub');
  client = {
    isOpen: false,
    connect: async () => {},
    get: async () => null,
    set: async () => {},
    del: async () => {}
  };
}

module.exports = client;

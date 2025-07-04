const fs = require('fs');
const path = require('path');
const logger = require('./logger');
const sensitiveKeyRegex = /(apiKey|credentialId|voiceId)/i;

class ConfigManager {
  constructor(env = process.env, configPath = path.join(__dirname, '..', 'config.json')) {
    this.env = env;
    this.fileConfig = {};
    if (fs.existsSync(configPath)) {
      try {
        this.fileConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      } catch (err) {
        logger.warn(`Failed to load config file ${configPath}: ${err.message}`);
      }
    }
    this.config = new Map();
    // Callbacks registered in this map will be notified on configuration
    // changes. Use '*' as the key to register a wildcard watcher that
    // is invoked for every change.
    this.watchers = new Map();
    this.setDefaults();
  }

  setDefaults() {
    this.config.set('video.processing.timeout', 300000);
    this.config.set('content.generation.retries', 3);
    this.config.set('cache.ttl.default', 3600);
    this.config.set('circuit.breaker.threshold', 5);
    this.config.set('rate.limit.requests', 100);
    this.config.set('rate.limit.window', 60000);
    this.config.set('health.check.interval', 30000);

    this.loadValue('openai.apiKey');
    this.loadValue('runwayml.apiKey');
    this.loadValue('openrouter.apiKey');
    this.loadValue('elevenlabs.apiKey');
    this.loadValue('elevenlabs.voiceId');
    this.loadValue('googleSheets.credentialId');
    this.loadValue('googleSheets.accountName');
    this.loadValue('youtube.credentialId');
    this.loadValue('youtube.accountName');
  }

  loadValue(key) {
    const envKey = key.toUpperCase().replace(/\./g, '_');
    let value = this.env[envKey];
    if (value === undefined) {
      value = this.fileConfig[key];
    }
    if (!value) {
      value = null;
      logger.warn(`Missing value for ${key}`);
    }
    this.config.set(key, value);
  }

  get(key, defaultValue = null) {
    return this.config.has(key) ? this.config.get(key) : defaultValue;
  }

  set(key, value) {
    const oldValue = this.config.get(key);
    this.config.set(key, value);
    // Notify watchers registered for this key and any global watchers
    // registered under '*' which acts as a wildcard for all keys.
    const watchers = [
      ...(this.watchers.get(key) || []),
      ...(this.watchers.get('*') || [])
    ];
    const maskedOld = sensitiveKeyRegex.test(key) && typeof oldValue === 'string' ? `${oldValue.slice(0,3)}...` : oldValue;
    const maskedNew = sensitiveKeyRegex.test(key) && typeof value === 'string' ? `${value.slice(0,3)}...` : value;
    for (const watcher of watchers) {
      try {
        watcher(key, maskedNew, maskedOld);
      } catch (err) {
        logger.error('Config watcher error', { key, error: err.message });
      }
    }
  }

  watch(key, callback) {
    // Use '*' as the key to subscribe to changes for all configuration keys
    if (!this.watchers.has(key)) this.watchers.set(key, []);
    this.watchers.get(key).push(callback);
  }

  getAll(maskSensitive = false) {
    const obj = {};
    for (const [k, v] of this.config.entries()) {
      obj[k] = maskSensitive && sensitiveKeyRegex.test(k) && typeof v === 'string' ? `${v.slice(0,3)}...${v.slice(-3)}` : v;
    }
    return obj;
  }
}

module.exports = ConfigManager;

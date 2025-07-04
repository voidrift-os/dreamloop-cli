const { v4: uuidv4 } = require('uuid');
const logger = require('./logger');

class EventBus {
  constructor() {
    this.listeners = {};
  }

  generateId() {
    return uuidv4();
  }
  subscribe(type, handler) {
    if (!this.listeners[type]) this.listeners[type] = new Set();
    this.listeners[type].add(handler);
    return () => this.listeners[type].delete(handler);
  }
  emit(type, data) {
    if (this.listeners[type]) {
      for (const handler of this.listeners[type]) {
        try {
          handler(data);
        } catch (err) {
          logger.error('Unhandled handler error', { event: type, error: err.message });
        }
      }
    }
  }
}

class EnhancedEventBus extends EventBus {
  constructor() {
    super();
    this.deadLetterQueue = [];
    this.maxRetries = 3;
    this.retryDelays = [1000, 5000, 15000];
  }

  emit(type, data) {
    const listeners = this.listeners[type];
    if (!listeners) return;
    for (const handler of listeners) {
      this.executeHandler(handler, { type, data, retryCount: 0 });
    }
  }

  executeHandler(handler, message) {
    const { retryCount } = message;
    try {
      Promise.resolve(handler({ ...message.data })).catch(err => {
        this.handleFailure(handler, message, err);
      });
    } catch (err) {
      this.handleFailure(handler, message, err);
    }
  }

  handleFailure(handler, message, error) {
    const retryCount = message.retryCount || 0;
    logger.error(`Handler failed for ${message.type}`, { error: error.message });
    if (retryCount < this.maxRetries) {
      const delay = this.retryDelays[retryCount] || this.retryDelays[this.retryDelays.length - 1];
      try {
        setTimeout(() => this.executeHandler(handler, { ...message, retryCount: retryCount + 1 }), delay);
      } catch (e) {
        logger.error('Failed to schedule retry', { error: e.message });
        this.pushToDeadLetter(message, error);
      }
    } else {
      this.pushToDeadLetter(message, error);
    }
  }

  pushToDeadLetter(message, error) {
    const id = uuidv4();
    const record = { id, ...message, error: error.message, failedAt: Date.now() };
    this.deadLetterQueue.push(record);
    super.emit('message.dead_letter', { message: record });
  }

  getDeadLetterMessages() {
    return this.deadLetterQueue;
  }

  reprocessDeadLetter(id) {
    const index = this.deadLetterQueue.findIndex(m => m.id === id);
    if (index === -1) return false;
    const msg = this.deadLetterQueue.splice(index, 1)[0];
    this.executeHandler(() => this.emit(msg.type, msg.data), { type: msg.type, data: msg.data, retryCount: 0 });
    return true;
  }
}

module.exports = { EventBus, EnhancedEventBus };

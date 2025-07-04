const { EnhancedEventBus } = require('../src/eventBus');

describe('EnhancedEventBus', () => {
  test('moves failing messages to dead letter and can reprocess', () => {
    const bus = new EnhancedEventBus();
    bus.maxRetries = 0;
    bus.retryDelays = [0];

    const failingHandler = () => { throw new Error('boom'); };
    bus.subscribe('test', failingHandler);
    bus.emit('test', { foo: 'bar' });

    const messages = bus.getDeadLetterMessages();
    expect(messages.length).toBe(1);
    const id = messages[0].id;
    expect(messages[0].type).toBe('test');

    const successHandler = jest.fn();
    bus.subscribe('test', successHandler);
    const result = bus.reprocessDeadLetter(id);

    expect(result).toBe(true);
    expect(successHandler).toHaveBeenCalled();
    expect(bus.getDeadLetterMessages().length).toBe(0);
  });
});

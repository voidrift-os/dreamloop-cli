const RateLimiter = require('../src/rateLimiter');

describe('RateLimiter', () => {
  test('throws when request limit exceeded', () => {
    const rl = new RateLimiter(2, 1000, 1000, 10);
    rl.checkLimit('user');
    rl.checkLimit('user');
    expect(() => rl.checkLimit('user')).toThrow('Rate limit exceeded');
  });

  test('cleanup removes old entries', () => {
    jest.useFakeTimers();
    const rl = new RateLimiter(2, 1000, 1000, 10);
    rl.checkLimit('user');
    jest.advanceTimersByTime(1500);
    rl.cleanup();
    expect(() => rl.checkLimit('user')).not.toThrow();
    jest.useRealTimers();
  });
});

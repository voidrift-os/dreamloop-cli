const request = require('supertest');

// Set API key for the server before it is required
process.env.API_KEY = 'test-key';

const app = require('../src/app');

describe('/process-video endpoint', () => {
  test('returns correlationId for valid request', async () => {
    const res = await request(app)
      .post('/process-video')
      .set('x-api-key', 'test-key')
      .send({ promptParams: { topic: 'test' }, options: { priority: 'high', userId: 'u1' } });
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('correlationId');
  });

  test('returns 400 when request body is invalid', async () => {
    const res = await request(app)
      .post('/process-video')
      .set('x-api-key', 'test-key')
      .send({});
    expect(res.status).toBe(400);
  });
});

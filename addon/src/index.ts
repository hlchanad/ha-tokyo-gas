import Fastify from 'fastify';
import { TokyoGasScraper } from './tokyo-gas-scraper';

const fastify = Fastify({
  logger: true
});

fastify.get(
  '/electricity-usages',
  {
    schema: {
      querystring: {
        type: 'object',
        properties: {
          username: { type: 'string' },
          password: { type: 'string' },
          customerNumber: { type: 'string' },
        },
        required: ['username', 'password', 'customerNumber'],
      },
    },
  },
  async (req, res) => {
    fastify.log.info('Retrieving electricity usages');

    const { username, password, customerNumber } = req.query as { username: string; password: string; customerNumber: string };

    const scraper = await TokyoGasScraper(username, password, customerNumber, fastify.log);
    await scraper.login();

    return [{ foo: 'bar'} ];
  },
);

const port = 3000;
fastify.listen({ host: '0.0.0.0', port })
  .catch(err => {
    fastify.log.error(err);
    process.exit(1);
  });

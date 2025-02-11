import Fastify from 'fastify';
import { TokyoGasScraper } from './tokyo-gas-scraper';

const fastify = Fastify({
  logger: true
});

fastify.post(
  '/login',
  {
    schema: {
      body: {
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
    const { username, password, customerNumber } = req.body as { username: string; password: string; customerNumber: string  };

    const scraper = await TokyoGasScraper(username, password, customerNumber, fastify.log);
    const result = await scraper.verifyCredentials();

    if (!result) {
      return res.status(401).send();
    }

    return res.status(204).send();
  }
)

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
          date: { type: 'string', format: 'date' },
        },
        required: ['username', 'password', 'customerNumber', 'date'],
      },
    },
  },
  async (req, res) => {
    const { username, password, customerNumber, date } = req.query as { username: string; password: string; customerNumber: string; date: string };

    const scraper = await TokyoGasScraper(username, password, customerNumber, fastify.log);
    return scraper.fetchElectricityUsage(date);
  },
);

const port = 3000;
fastify.listen({ host: '0.0.0.0', port })
  .catch(err => {
    fastify.log.error(err);
    process.exit(1);
  });

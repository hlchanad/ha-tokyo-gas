import Fastify from 'fastify';

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

    fastify.log.info(`query: ${JSON.stringify(req.query)}`);

    return [{ foo: 'bar'} ];
  },
);

const port = 3000;
fastify.listen({ host: '0.0.0.0', port })
  .catch(err => {
    fastify.log.error(err);
    process.exit(1);
  });

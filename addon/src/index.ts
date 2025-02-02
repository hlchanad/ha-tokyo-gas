import Fastify from 'fastify';

const fastify = Fastify({
  logger: true
});

fastify.get('/electricity-usages', async (req, res) => {
  fastify.log.info('Retrieving electricity usages');
  return [{ foo: 'bar'} ];
});

const port = 3000;
fastify.listen({ host: '0.0.0.0', port })
  .catch(err => {
    fastify.log.error(err);
    process.exit(1);
  });

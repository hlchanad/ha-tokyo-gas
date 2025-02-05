import { FastifyBaseLogger } from 'fastify';

export type Logger = FastifyBaseLogger;

export type Usage = {
  date: string;
  usage: number;
};

import { PinoLoggerOptions } from 'fastify/types/logger';
import fs from 'fs';

type Config = {
  port: number;
  log_level: PinoLoggerOptions['level'];
};

let options: Config | undefined = undefined;

function readOptions(): Config {
  if (!fs.existsSync('/data/options.json')) {
    throw new Error('options.json is missing');
  }

  const content = fs.readFileSync('/data/options.json');

  console.log('/data/options.json', content.toString());

  return JSON.parse(content.toString()) as Config;
}

export function getOptions(): Config {
  if (!options) {
    options = readOptions();
  }

  return options;
}
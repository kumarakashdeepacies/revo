import babel from 'rollup-plugin-babel';
import { terser } from 'rollup-plugin-terser';
import { version } from './package.json';

const banner = `/**
 * @name creditcard.js ${version}
 * @license MIT
 * @author ContaAzul (contaazul.com)
 */`;

export default {
  input: 'src/creditcard.js',
  output: [
    {
      banner,
      compact: true,
      file: 'dist/creditcard.js',
      format: 'umd',
      name: 'CreditCard',
    },
    {
      banner,
      file: 'dist/creditcard.min.js',
      format: 'cjs',
      name: 'CreditCard',
      plugins: [terser()],
    },
  ],
  plugins: [
    babel({
      exclude: 'node_modules/**',
    }),
  ],
  watch: {
    exclude: 'node_modules/**',
  },
};

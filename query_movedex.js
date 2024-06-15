const {Dex} = require('pokemon-showdown');
const {program} = require('commander');
const jsyaml = require('js-yaml');
const fs = require('fs')

program
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--move <string>', 'Move to search.')
  .parse()

const options = program.opts();
const move = Dex.mod('gen1').moves.get(options.move);

console.log(options.move); 
fs.writeFile("config/moves/" + options.move + ".yaml", jsyaml.dump(move, {'skipInvalid': true}), (err) => {
    // In case of a error throw err.
    if (err) throw err;
})

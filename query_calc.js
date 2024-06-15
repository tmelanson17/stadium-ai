const calc = require("@smogon/calc")
const {program} = require('commander');
const jsyaml = require('js-yaml');
const fs = require('fs')


program
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--attacker <string>', 'Attacking pokemon.')
  .option('-al, --attacking_level <number>', ' Attacking pokemon level.')
  .option('--defender <string>', 'Defending pokemon.')
  .option('-dl, --defending_level <number>', ' Defending pokemon level.')
  .option('-m, --move <string>', "Move")
  .parse();

const options = program.opts();
console.log("Calculating attack:")
console.log(options.attacker)
console.log(options.attacking_level)
console.log(options.defender)
console.log(options.defending_level)

// TODO: Take into account dv's / raw stats
// TODO: Take into acccount stat boosts.
const gen = calc.Generations.get(1); 
const result = calc.calculate(
  gen,
  new calc.Pokemon(gen, options.attacker, {
    level: parseInt(options.attacking_level),
  }),
  new calc.Pokemon(gen, options.defender, {
    level: parseInt(options.defending_level),
  }),
  new calc.Move(gen, options.move)
);
console.log(result)
fs.writeFile("query_result.yaml", jsyaml.dump(result), (err) => {
    // In case of a error throw err.
    if (err) throw err;
})

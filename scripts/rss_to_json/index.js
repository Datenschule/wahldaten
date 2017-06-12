const program = require('commander');

program
	.version('0.0.1')
	.arguments('<file>')
	.option('-o --out', 'Specifiy output file, standard is out.json')
	.parse(process.argv);

// if (program.file) {
	console.log('file: ' + program.arguments);
	program.output ? console.log('out: ' + program.out) : console.log('out: out.json');
// } else {
// 	console.log('file not found');
// 	program.outputHelp();
// }
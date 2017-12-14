var abi = require('ethereumjs-abi')

var parameterTypes = ["string", "address"];
var parameterValues = ["TestPoll", "0x00258584ffc280EE6194d92D635D8015679b58e7"];

var encoded = abi.rawEncode(parameterTypes, parameterValues);

console.log(encoded.toString('hex'));

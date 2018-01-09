pragma solidity ^0.4.0;

contract QuestionaryStorage {

    address public owner;
    mapping (address => (string => string) public answers;

    function saveAnswers(string voteAnswers) public onlyBy(owner)
    {
        answers = voteAnswers;
    }




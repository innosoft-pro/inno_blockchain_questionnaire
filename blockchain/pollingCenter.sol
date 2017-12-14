pragma solidity ^0.4.0;

contract UfaPollingCenter {

    address public owner;
    
    mapping (string=>Poll) polls;

    event PollCreated(string, Poll);

    function UfaPollingCenter() public {
        owner = msg.sender;
    }
    
    function getPollByName(string pollName) public constant
    returns (Poll) 
    {
        return polls[pollName];
    }
    
    function createPoll(string pollName) public onlyBy(owner)
    returns (bool)
    {
        if (polls[pollName] != address(0))
            return false;

        polls[pollName] = new Poll(pollName, owner);
        PollCreated(pollName, polls[pollName]);
        return true;
    }

    modifier onlyBy(address _account)
    {
        require(msg.sender == _account);
        _;
    }
}

contract Poll {
    address public owner;
    
    string public pollName;
    
    struct Answer {
        uint rating;
        uint[] ans;
    }
    
    //mapping (uint => uint[]) public answers;
    mapping (uint => Answer) private answers;
    
    event AnswersRecorded(uint);
    event RatingChanged(uint, uint);
    
    function Poll(string _pollName, address _owner) public {
        owner = _owner;
        pollName = _pollName;
    }
    
    function getAnswersById(uint id) public constant
    returns (uint[])
    {
        return answers[id].ans;
    }
    
    function getRatingById(uint id) public constant
    returns (uint)
    {
        return answers[id].rating;
    }
    
    function recordAnswers(uint id, uint[] _ans) public onlyBy(owner)
    {
        answers[id].ans = _ans;
        answers[id].rating = 0;
        AnswersRecorded(id);
    }
    
    function changeRating(uint id, uint _rating) public onlyBy(owner)
    {
        answers[id].rating = _rating;
        RatingChanged(id, _rating);
    }
    
    modifier onlyBy(address _account)
    {
        require(msg.sender == _account);
        _;
    }
}

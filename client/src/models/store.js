import {types, flow, getEnv} from "mobx-state-tree";

const User = types.model("User", {
    name: types.string,
    password: types.string
});

const Question = types.model("Question", {
    text: types.string,
    type: types.enumeration(["open", "select", "multiselect"]),
    options: types.maybe(types.array(types.string))
});

const Poll = types.model("Poll", {
    _id: types.maybe(types.string),
    name: types.string,
    archived: types.boolean,
    participants: types.array(types.string),
    questions: types.array(Question)
});

export const Store = types.model("Store", {
    user: types.maybe(User),
    polls: types.array(Poll),
    isLoading: false
}).actions(self => {
    const login = flow(function* login(user) {
        self.user = user;
        return yield fetchPolls();
    })

    function getById(id) {
        const poll = self
            .polls
            .find(poll => poll._id === id);
        return poll || Poll.create({name: '', archived: false, participants: [], questions: []});
    }

    function markLoading(loading) {
        self.isLoading = loading
    }

    function savePoll(values) {
        const index = self
            .polls
            .findIndex(poll => poll._id === values._id);
        if (index >= 0) {
            self.polls[index].name = values.name;
            self.polls[index].participants = values.participants;
            self.polls[index].archived = values.archived;
            self.polls[index].questions = values.questions;
        } else {
            self
                .polls
                .push(values);
        }
    }

    const postPoll = flow(function* postPoll(values) {
        markLoading(true);
        try {
            const payload = {
                archived: values.archived,
                name: values.name,
                participants: values.participants,
                questions: values.questions || [],
            };
            if(values._id) {
                payload._id = values._id;
            }
            const json = yield getEnv(self).fetch('poll', {
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Authorization': 'Basic ' + btoa(self.user.name + ':' + self.user.password)
                  },
                  mode: 'cors',
                  method: "POST",
                  body: JSON.stringify(payload)
            });
            if( json ) {
                if( json.error ) {
                    getEnv(self).error({
                        title: "Error",
                        content: json.error
                    });
                } else {
                    savePoll(Object.assign({
                        questions: []
                    }, json));
                    getEnv(self)
                        .routing
                        .push('/list/' + json._id);
                }
            }
        } catch (err) {
            console.log('error', err);
        }
        markLoading(false);        
    });

    const fetchPolls = flow(function* fetchPolls() {
        markLoading(true);
        try {
            const json = yield getEnv(self).fetch('polls', {
                headers: {
                    'Accept': 'application/json',
                    'Authorization': 'Basic ' + btoa(self.user.name + ':' + self.user.password)
                  },
                  mode: 'cors',
                  method: "GET"
            });
            markLoading(false);   
            if( json ) {
                if( json.error ) {
                    getEnv(self).error({
                        title: "Error",
                        content: json.error
                    });
                } else {
                    self.polls = json.polls;
                    return true;
                }
            }
        } catch (err) {
            console.log('error', err);
        }
        markLoading(false);
        self.user.password = '';
    });

    return { postPoll, login, getById, fetchPolls };
});


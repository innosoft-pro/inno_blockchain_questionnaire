import { types } from "mobx-state-tree";
import { RouterStore } from 'mobx-react-router';

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
}).actions(self => ({
    login(user) {
        self.user = user;
    },
    getById(id) {
        const poll = self.polls.find( poll => poll._id == id);
        return poll || Poll.create({name: '', archived: false, participants: [], questions: []});
    }
}))

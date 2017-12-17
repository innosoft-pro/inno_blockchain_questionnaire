import { types } from "mobx-state-tree";

const User = types.model("User", {
    name: types.string,
    password: types.string
});

export const Store = types.model("Store", {
    user: types.maybe(User)
}).actions(self => ({
    login(user) {
        self.user = user;
    }
}));

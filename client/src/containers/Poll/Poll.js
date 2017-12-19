import React from "react";
import {decl} from "bem-react-core";
import {observer, inject} from "mobx-react";
import PollForm from "b:PollForm";

export default decl({
    block: "Poll",

    willInit() {
        this.onSubmit = this
            .onSubmit
            .bind(this);
    },

    content({match, store}) {
        const id = match.params.pollId;
        const poll = store.getById(id);
        return <PollForm poll={poll} onSubmit={this.onSubmit}/>;
    },

    onSubmit(values) {
        this.props.store.postPoll(values);
    }
}, (me) => {
    return inject("store")(observer(me));
});

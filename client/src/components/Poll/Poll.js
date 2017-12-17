import React from "react";
import { decl } from "bem-react-core";
import { observer, inject } from "mobx-react";

export default decl({
  block: "Poll",
  content({match, store}) {
      const id = match.params.pollId;
      const poll = store.getById(id);
      return "Poll " + poll.name;
  }
}, (me)=>{
    return inject("store")(observer(me));
});

import React from "react";
import { decl } from "bem-react-core";

export default decl({
  block: "Poll",
  content({match}) {
      return "Poll " + match.params.pollId;
  }
});

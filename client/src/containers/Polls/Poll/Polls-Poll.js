import React from "react";
import { Icon } from "antd";
import { decl } from "bem-react-core";

export default decl({
  block: "Polls",
  elem: "Poll",

  mods({ archived }) {
    return { archived: archived };
  },

  content({ name }) {
    return [<Icon type="pie-chart" key="i" />, <span key="n">{name}</span>];
  }
});


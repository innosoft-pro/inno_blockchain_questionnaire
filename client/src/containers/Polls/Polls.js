import React from "react";
import { decl } from "bem-react-core";
import { Menu, Button, Icon } from "antd";
import { observer, inject } from "mobx-react";
import Poll from "e:Poll m:archived";
import { withRouter } from "react-router";

export default decl(
  {
    block: "Polls",

    willInit() {
      this.selectPoll = this.selectPoll.bind(this);
    },

    content({ store, routing, match }) {
      const id = match.params.pollId;
      return [
        <center key="b">
          <Button
            type="primary"
            style={{ margin: "10px 0" }}
            onClick={() => {
              this.selectPoll({ key: "new" });
            }}
          >
            <Icon type="plus-square-o" />New Poll
          </Button>
        </center>,
        <Menu
          mode="inline"
          key="m"
          onClick={this.selectPoll}
          selectedKeys={[id]}
        >
          {store.polls.map(this.drawPoll)}
        </Menu>
      ];
    },

    drawPoll(poll, index) {
      return (
        <Menu.Item key={poll._id}>
          <Poll {...poll} />
        </Menu.Item>
      );
    },

    selectPoll({ key }) {
      this.props.routing.push("/polls/" + key);
    }
  },
  me => {
    return inject("store", "routing")(withRouter(observer(me)));
  }
);

import React from "react";
import {Layout} from "antd";
import {decl} from "bem-react-core";
import Polls from "b:Polls";
import Poll from "b:Poll";
import {Route, Switch} from "react-router-dom";

const {Sider, Content} = Layout;

export default decl({
  block: "IndexPage",

  content({match}) {
    return (
      <Layout style={{
        width: "100%"
      }}>
        <Sider style={{
          background: "#fff"
        }}>
          <Polls/>
        </Sider>
        <Content>
          <Switch>
            <Route exact path="/polls/:pollId" component={Poll}/>
          </Switch>
        </Content>
      </Layout>
    );
  }
});

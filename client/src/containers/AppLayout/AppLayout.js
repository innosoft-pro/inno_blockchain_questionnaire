import React from 'react';
import './AppLayout.css';
import {Layout} from 'antd';
import {decl} from 'bem-react-core';
const {Header, Footer, Content} = Layout;

export default decl({
  block: 'AppLayout',

  content() {
    return (
      <Layout className="Layout">
        <Header>Header</Header>
        <Content className="Content">
          {this.props.children}
        </Content>
        <Footer className="Footer">Footer</Footer>
      </Layout>
    );
  }
});

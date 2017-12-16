import React, {Component} from 'react';
import './AppLayout.css';
import {Layout} from 'antd';

const {Header, Footer, Sider, Content} = Layout;

class AppLayout extends Component {
  render() {
    return (
      <div className="App">
        <Layout className="Layout">
          <Header>Header</Header>
          <Content className="Content">
            {this.props.children}
          </Content>
          <Footer className="Footer">Footer</Footer>
        </Layout>
      </div>
    );
  }
}

export default AppLayout;

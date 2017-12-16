import React, {Component} from 'react';
import logo from './logo.svg';
import './App.css';
import {Layout} from 'antd';
import IndexPage from './containers/IndexPage/IndexPage';

const {Header, Footer, Sider, Content} = Layout;

class App extends Component {
  render() {
    return (
      <div className="App">
        <Layout className="Layout">
          <Header>Header</Header>
          <Content className="Content">
            <IndexPage/>
          </Content>
          <Footer className="Footer">Footer</Footer>
        </Layout>
      </div>
    );
  }
}

export default App;

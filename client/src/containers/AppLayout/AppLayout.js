import React from 'react';
import './AppLayout.css';
import {Layout, Icon} from 'antd';
import {decl} from 'bem-react-core';
const {Header, Footer, Content} = Layout;

export default decl({
  block: 'AppLayout',

  content() {
    return (
      <Layout className="Layout">
        <Header className="Header"><a href="/"><Icon type="aliwangwang-o" className="Logo" /> Le`Questionnaire</a></Header>
        <Content className="Content">
          {this.props.children}
        </Content>
        <Footer className="Footer"><a target="_blank" href="http://innosoft.pro">©&nbsp;Innosoft, 2017</a></Footer>
      </Layout>
    );
  }
});

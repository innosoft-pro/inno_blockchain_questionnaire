import React from 'react';
import './AppLayout.css';
import {Layout, Icon} from 'antd';
import {decl} from 'bem-react-core';
import {Link} from 'react-router-dom';
const {Header, Footer, Content} = Layout;

export default decl({
  block: 'AppLayout',

  content() {
    return (
      <Layout className="Layout">
        <Header className="Header"><Link to="/"><Icon type="aliwangwang-o" className="Logo" /> Le`Questionnaire</Link></Header>
        <Content className="Content">
          {this.props.children}
        </Content>
        <Footer className="Footer"><a target="_blank" rel="noopener noreferrer" href="http://innosoft.pro">©&nbsp;Innosoft, 2017</a></Footer>
      </Layout>
    );
  }
});

import React from "react";
import LoginForm from "b:LoginForm";
import {inject} from "mobx-react";
import {decl} from "bem-react-core";
import {Modal} from 'antd';

export default decl({
  block: "LoginPage",

  willInit() {
    this.onLogin = this.onLogin.bind(this);
  },

  content({store}) {
    return [ 
      (<h1 key = "h" > Welcome !</h1>), 
      (<LoginForm key = "f" onLogin = {this.onLogin} />)
    ];
  },

  onLogin(values) {
    this
      .props
      .store
      .login({name: values.userName, password: values.password})
      .then(ok => {
        if (ok) {
          this
            .props
            .routing
            .replace(this.props.routing.location.state.from);
        } else {
          Modal.error({
            title: 'Could not fetch polls',
            content: (
              <div>
                <p>Possibly wrong login or password</p>
              </div>
            ),
            onOk() {},
          });
        }
      });
  }
}, me => {
  return inject("store", "routing")(me);
});

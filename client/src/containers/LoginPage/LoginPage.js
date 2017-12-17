import React from "react";
import LoginForm from "b:LoginForm";
import { inject } from "mobx-react";
import { decl } from "bem-react-core";

export default decl(
  {
    block: "LoginPage",

    willInit() {
      this.onLogin = this.onLogin.bind(this);
    },

    content() {
      return [
        <h1 key="h">Welcome!</h1>,
        <LoginForm key="f" onLogin={this.onLogin} />
      ];
    },

    onLogin(values) {
      this.props.store.login({
        name: values.userName,
        password: values.password
      });
      this.props.routing.replace(this.props.routing.location.state.from);
    }
  },
  me => {
    return inject("store", "routing")(me);
  }
);

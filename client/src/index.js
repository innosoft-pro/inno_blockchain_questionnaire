import React, { Component } from "react";
import ReactDOM from "react-dom";
import registerServiceWorker from "./registerServiceWorker";
import { BrowserRouter as Router, Route, Redirect } from "react-router-dom";
import 'b:Page';
import AppLayout from "b:AppLayout";
import IndexPage from "b:IndexPage";
import LoginPage from "b:LoginPage";

const PrivateRoute = ({ component: Component, ...rest }) => (
  <Route
    {...rest}
    render={props =>
      true ? (
        <Component {...props} />
      ) : (
        <Redirect
          to={{
            pathname: "/login",
            state: { from: props.location }
          }}
        />
      )
    }
  />
);

class Routes extends Component {
  render() {
    return (
      <Router>
        <AppLayout>
          <PrivateRoute exact path="/" component={IndexPage} />
          <Route path="/login" component={LoginPage} />
        </AppLayout>
      </Router>
    );
  }
}

ReactDOM.render(<Routes />, document.getElementById("root"));
registerServiceWorker();

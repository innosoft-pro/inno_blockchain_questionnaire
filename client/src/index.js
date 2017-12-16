import React, { Component } from "react";
import ReactDOM from "react-dom";
import AppLayout from "./containers/AppLayout/AppLayout";
import registerServiceWorker from "./registerServiceWorker";
import { BrowserRouter as Router, Route, Redirect } from "react-router-dom";
import IndexPage from "./containers/IndexPage/IndexPage";
import LoginPage from "./containers/LoginPage/LoginPage";
import 'b:Page';

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

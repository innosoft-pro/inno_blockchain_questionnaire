import React, { Component } from "react";
import ReactDOM from "react-dom";
import registerServiceWorker from "./registerServiceWorker";
import { BrowserRouter as Router, Route, Redirect } from "react-router-dom";
import { observer, inject } from "mobx-react";
import { Store } from "./models/store";
import { Provider } from "mobx-react";
import "b:Page";
import AppLayout from "b:AppLayout";
import IndexPage from "b:IndexPage";
import LoginPage from "b:LoginPage";
import Switch from "react-router-dom/Switch";

const fetcher = url => window.fetch(url).then(response => response.json());
const store = Store.create(
  {},
  {
    fetch: fetcher,
    alert: m => console.log(m) // Noop for demo: window.alert(m)
  }
);
// store.login({ name: "bitch", password: "nono" });
window.store = store;

const PrivateRoute = inject("store")(
  observer(({ store, component: Component, ...rest }) => (
    <Route
      {...rest}
      render={props =>
        store.user ? (
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
  ))
);

class Routes extends Component {
  render() {
    return (
      <Router>
        <Provider store={store}>
          <AppLayout>
            <Switch>
              <PrivateRoute exact path="/" component ={IndexPage} />
              <Route path="/login" component={LoginPage} />
            </Switch>
          </AppLayout>
        </Provider>
      </Router>
    );
  }
}

ReactDOM.render(<Routes />, document.getElementById("root"));
registerServiceWorker();

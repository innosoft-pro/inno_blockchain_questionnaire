import React, { Component } from "react";
import ReactDOM from "react-dom";
import registerServiceWorker from "./registerServiceWorker";
import { Router, Route, Redirect } from "react-router-dom";
import { observer, inject } from "mobx-react";
import { Store } from "./models/store";
import { Provider } from "mobx-react";
import "b:Page";
import AppLayout from "b:AppLayout";
import IndexPage from "b:IndexPage";
import LoginPage from "b:LoginPage";
import Switch from "react-router-dom/Switch";
import { RouterStore, syncHistoryWithStore } from "mobx-react-router";
import createBrowserHistory from "history/createBrowserHistory";

const browserHistory = createBrowserHistory();
const routingStore = new RouterStore();
const fetcher = url => window.fetch(url).then(response => response.json());
const store = Store.create(
  {
    polls: [
      {
        _id: "first",
        name: "Test poll tttoeuhhh oetetetetet ttetetetococ tototoc c",
        archived: false,
        participants: ['tttt', 'oeuoeuoeu'],
        questions: [
          {
            text: "First open question",
            type: "open"
          },
          {
            text: "second select q",
            type: "select",
            options: ["one", "two", "three"]
          },
          {
            text: "Third multi",
            type: "multiselect",
            options: ["1", "2", "3"]
          }
        ]
      },
      {
        _id: "second",
        name: "Archived one",
        archived: true,
        participants: [],
        questions: []
      }
    ], router: routingStore
  },
  {
    fetch: fetcher,
    alert: m => console.log(m) // Noop for demo: window.alert(m)
  }
);
store.login({ name: "admin", password: "secret" });
window.store = store;

const history = syncHistoryWithStore(browserHistory, routingStore);

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
      <Provider store={store} routing={routingStore}>
        <Router history={history}>
          <AppLayout>
            <Switch>
              <Redirect from="/" exact to="/polls" />
              <PrivateRoute path="/polls/:pollId?" component={IndexPage} />
              <Route path="/login" component={LoginPage} />
              <Redirect to="/polls" />
            </Switch>
          </AppLayout>
        </Router>
      </Provider>
    );
  }
}

ReactDOM.render(<Routes />, document.getElementById("root"));
registerServiceWorker();

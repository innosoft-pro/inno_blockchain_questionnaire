import React from "react";
import {decl} from "bem-react-core";
import {observer} from "mobx-react";
import {
  Form,
  Icon,
  Input,
  Button,
  Switch,
  Card,
  Table,
  Select
} from "antd";

const FormItem = Form.Item;
const Option = Select.Option;
const ButtonGroup = Button.Group;
const {TextArea} = Input;

export default decl({
  block: "PollForm",

  willInit() {
    this.handleSubmit = this
      .handleSubmit
      .bind(this);
    this.addQuestion = this
      .addQuestion
      .bind(this);
    this.loadAnswers = this
      .loadAnswers
      .bind(this);
  },

  addQuestion() {
    this
      .props
      .form
      .getFieldDecorator('size');
    const size = this
      .props
      .form
      .getFieldValue('size');
    this
      .props
      .form
      .setFieldsValue({
        'size': size + 1
      });
    this
      .props
      .form
      .getFieldDecorator('questions[' + size + '].text');
    this
      .props
      .form
      .setFieldsValue({
        ['questions[' + size + '].text']: ''
      });
    this
      .props
      .form
      .getFieldDecorator('questions[' + size + '].type');
    this
      .props
      .form
      .setFieldsValue({
        ['questions[' + size + '].type']: ''
      });
    this
      .props
      .form
      .getFieldDecorator('questions[' + size + '].options');
    this
      .props
      .form
      .setFieldsValue({
        ['questions[' + size + '].options']: []
      });
  },

  loadAnswers() {
    this.props.onLoadAnswers(this.props.poll._id);
  },

  content({poll}) {
    const {getFieldDecorator, getFieldValue} = this.props.form;
    const formItemLayout = {
      labelCol: {
        span: 6
      },
      wrapperCol: {
        span: 17
      }
    };
    window.form = this.props.form;
    const rules = [
      {
        required: true,
        message: "Please, enter value!"
      }
    ];
    const title = poll._id
      ? "Edit Poll #" + poll._id
      : "Create Poll";

    const columns = [
      {
        title: 'Text',
        dataIndex: 'text',
        width: 400,
        render: (text, record) => {
          return (
            <FormItem>
              {this
                .props
                .form
                .getFieldDecorator("questions[" + record.key + "].text", {
                  initialValue: record.text,
                  rules: rules
                })(<TextArea autosize/>)}
            </FormItem>
          );
        }
      }, {
        title: 'Type',
        dataIndex: 'type',
        render: (text, record) => {
          return (
            <FormItem>{this
                .props
                .form
                .getFieldDecorator("questions[" + record.key + "].type", {
                  initialValue: record.type,
                  rules: rules
                })(
                  <Select>
                    <Option value="open">Open question</Option>
                    <Option value="select">Options</Option>
                    <Option value="multiselect">Multiple options</Option>
                  </Select>
                )}</FormItem>
          );
        }
      }, {
        title: 'Options',
        dataIndex: 'options',
        render: (text, record) => {
          return this
            .props
            .form
            .getFieldDecorator("questions[" + record.key + "].options", {initialValue: record.options})(
              <Select mode="tags"></Select>
            );
        }
      }
    ];

    let questions = [];
    const size = getFieldValue('size');
    for (let i = 0; i < size; i++) {
      questions.push({
        key: i,
        type: getFieldValue('questions[' + i + '].type'),
        text: getFieldValue('questions[' + i + '].text'),
        options: getFieldValue('questions[' + i + '].options')
      });
    }

    getFieldDecorator('_id');

    var extra = poll._id && (
      <ButtonGroup>
        <Button type="primary" icon="dot-chart" onClick={this.loadAnswers}>View answers</Button>
        <Button
          //href={"http://localhost:5000/api/download?poll_id=" + poll._id}
          href={"/api/download?poll_id=" + poll._id}
          target="_blank"
          icon="download"
          type="dashed">Download answers</Button>
      </ButtonGroup>
    );

    return (
      <div>
        <Card className="Card" title={title}>
          <Form onSubmit={this.handleSubmit} className="login-form">
            <FormItem label="Poll Name" required={true} {...formItemLayout}>
              {getFieldDecorator("name", {
                rules: [
                  {
                    required: true,
                    message: "Please input poll name!"
                  }
                ]
              })(<Input required={true} placeholder="Poll name"/>)}
            </FormItem>
            <FormItem label="Welcome message" required={true} {...formItemLayout}>
              {getFieldDecorator("welcome_message", {
                rules: [
                  {
                    required: true,
                    message: "Please input welcome message!"
                  }
                ]
              })(<Input required={true} rows={4} placeholder="Greeting message"/>)}
            </FormItem>
            <FormItem label="Participants" {...formItemLayout}>
              {getFieldDecorator("participants", {})(<Select mode="tags" placeholder="Participants"/>)}
            </FormItem>
            <FormItem {...formItemLayout} label="Archived">
              {getFieldDecorator('archived', {valuePropName: "checked"})(<Switch checkedChildren="yes"/>)}
            </FormItem>
            <FormItem>
              <Table
                columns={columns}
                dataSource={questions}
                bordered
                title={() => "Questions"}
                pagination = {false}
                footer={() => (
                <Button type="primary" size="small" onClick={this.addQuestion}><Icon type="plus"/>
                  Add</Button>
              )}/>
            </FormItem>
            <FormItem>
              <Button
                style={{
                width: "auto"
              }}
                type="primary"
                htmlType="submit"
                className="login-form-button">
                Save
              </Button>
            </FormItem>
          </Form>
        </Card>
        {poll._id && <Card className="Card" title="Answers" extra={extra}>
          <pre>{poll.answers}</pre>
        </Card>}
      </div>
    );
  },

  handleSubmit(e) {
    e.preventDefault();
    this
      .props
      .form
      .validateFields((err, values) => {
        if (!err) {
          this.props.onSubmit && this
            .props
            .onSubmit(values);
        }
      });
  }
}, (me) => {
  return Form.create({
    mapPropsToFields({poll}) {
      let props = {
        name: Form.createFormField({value: poll.name}),
        welcome_message: Form.createFormField({value: poll.welcome_message}),
        participants: Form.createFormField({
          value: poll
            .participants
            .slice()
        }),
        archived: Form.createFormField({value: poll.archived}),
        _id: Form.createFormField({value: poll._id})
      };
      const l = poll.questions.length;
      props["size"] = Form.createFormField({value: l});
      props["questions"] = Form.createFormField({value: []});
      for (let i = 0; i < l; i++) {
        const options = poll.questions[i].options || [];
        props["questions[" + i + "].text"] = Form.createFormField({value: poll.questions[i].text});
        props["questions[" + i + "].type"] = Form.createFormField({value: poll.questions[i].type});
        props["questions[" + i + "].options"] = Form.createFormField({
          value: options.slice()
        });
      }
      return props;
    }
  })(observer(me));
});

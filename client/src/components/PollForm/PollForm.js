import React from "react";
import {decl} from "bem-react-core";
import {
  Form,
  Icon,
  Input,
  Button,
  Checkbox,
  Row,
  Switch,
  Col,
  Card,
  Table,
  Select
} from "antd";

const FormItem = Form.Item;
const Option = Select.Option;
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
  },

  addQuestion() {
    this
      .props
      .form
      .getFieldDecorator("questions");
    let questions = this
      .props
      .form
      .getFieldValue('questions').slice();
    questions.push({text: '', type: 'open', options: []});

    this
      .props
      .form
      .setFieldsValue({
        questions: questions.map((q, ind) => {
          return Object.assign({
            key: ind
          }, q);
        })
      });
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
    const title = poll._id
      ? "Edit Poll #" + poll._id
      : "Create Poll";
    const columns = [
      {
        title: '#',
        dataIndex: 'key',
        render: (text, record) => {
          getFieldDecorator("questions[" + record.key + "]", {});
          return text;
        }
      },
      {
        title: 'Text',
        dataIndex: 'text',
        width: 400,
        render: (text, record) => {
          return getFieldDecorator("questions[" + record.key + "]", {valuePropName: 'text'})(<TextArea autosize/>);
        }
      }, {
        title: 'Type',
        dataIndex: 'type',
        render: (text, record) => {
          return  getFieldDecorator("questions[" + record.key + "].type", {initialValue: text})(
            <Select>
              <Option value="open">Open question</Option>
              <Option value="select">Options</Option>
              <Option value="multiselect">Multiple options</Option>
            </Select>
          );
        }
      }, {
        title: 'Options',
        dataIndex: 'options',
        render: (text, record) => {
          const value = text && text.slice() || [];
          return getFieldDecorator("questions[" + record.key + "].options", {initialValue: value})(
            <Select mode="tags"></Select>
          );
        }
      }
    ];

    const questions = getFieldValue('questions');
    console.log('data', questions);

    return (
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
    );
  },

  handleSubmit(e) {
    e.preventDefault();
    this
      .props
      .form
      .validateFields((err, values) => {
        if (!err) {
          console.log("Received values of form: ", values);
        }
      });
  }
}, (me) => {
  return Form.create({
    mapPropsToFields({poll}) {
      return {
        name: Form.createFormField({value: poll.name}),
        participants: Form.createFormField({
          value: poll
            .participants
            .slice()
        }),
        archived: Form.createFormField({value: poll.archived}),
        questions: Form.createFormField({
          value: poll.questions && poll
            .questions
            .slice()
            .map((q, index) => {
              return {
                key: index,
                text: q.text,
                type: q.type,
                options: q.options && q
                  .options
                  .slice() || []
              };
            }) || []
        })
      };
    }
  })(me);
});

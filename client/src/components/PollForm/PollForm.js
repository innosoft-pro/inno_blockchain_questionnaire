import React from "react";
import {decl} from "bem-react-core";
import {observer} from "mobx-react";
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
      .setFieldsValue({
        ['questions[' + size + '].text']: ''
      });
    this
      .props
      .form
      .setFieldsValue({
        ['questions[' + size + '].type']: ''
      });
    this
      .props
      .form
      .setFieldsValue({
        ['questions[' + size + '].options']: []
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
    window.form = this.props.form;
    const title = poll._id
      ? "Edit Poll #" + poll._id
      : "Create Poll";

    const columns = [
      {
        title: 'Text',
        dataIndex: 'text',
        width: 400,
        render: (text, record) => {
          return this
            .props
            .form
            .getFieldDecorator("questions[" + record.key + "].text", {initialValue: record.text})(<TextArea autosize/>);
        }
      }, {
        title: 'Type',
        dataIndex: 'type',
        render: (text, record) => {
          return this
            .props
            .form
            .getFieldDecorator("questions[" + record.key + "].type", {initialValue: record.type})(
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
  return observer(Form.create({
    mapPropsToFields({poll}) {
      let props = {
        name: Form.createFormField({value: poll.name}),
        participants: Form.createFormField({
          value: poll
            .participants
            .slice()
        }),
        archived: Form.createFormField({value: poll.archived})
      };
      const l = poll.questions.length;
      props["size"] = Form.createFormField({value: l});
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
  })(me));
});

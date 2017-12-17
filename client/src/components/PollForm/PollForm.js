import React from "react";
import { decl } from "bem-react-core";
import { Form, Icon, Input, Button, Checkbox, Row, Col } from "antd";

const FormItem = Form.Item;
export default decl(
  {
    block: "PollForm",

    content({ poll }) {
      const { getFieldDecorator } = this.props.form;
      const formItemLayout = {
        labelCol: {
            sm: { span: 4, offset: 4 },
            xs: { span: 24 }
        },
        wrapperCol: { 
            sm: { span: 10 },
            xs: { span: 24 }
        }
      };

      return (
        <Form onSubmit={this.handleSubmit} className="login-form">
          <FormItem label="Poll Name" required={true} {...formItemLayout}>
            {getFieldDecorator("name", {
              rules: [{ required: true, message: "Please input poll name!" }]
            })(<Input required={true} placeholder="Poll name" />)}
          </FormItem>
          <FormItem label="Participants" {...formItemLayout}>
            {getFieldDecorator("participants", {})(
              <Input placeholder="Participants" />
            )}
          </FormItem>
        </Form>
      );
    },

    handleSubmit(e) {
      e.preventDefault();
      this.props.form.validateFields((err, values) => {
        if (!err) {
          console.log("Received values of form: ", values);
        }
      });
    }
  },
  me => {
    return Form.create({
      mapPropsToFields({ poll }) {
        return {
          name: Form.createFormField({
            value: poll.name
          }),
          participants: Form.createFormField({
            value: poll.participants.join(",")
          })
        };
      }
    })(me);
  }
);

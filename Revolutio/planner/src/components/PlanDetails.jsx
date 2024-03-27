import * as React from "react";
import { ReactDOM } from "react";
import PlanColumn from "./PlanColumn";
import axios from "axios";

class PlanDetails extends React.Component{
    constructor(props){
        super(props);
    }

    addColumn=(plan)=>{
        var planName = plan.plan_name;
        var bucketName = "New column";
        var bucketId = ("column"+Math.random()).replace('.','');
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value
        const configHeaders = {
            "content-type": "application/json",
            "Accept": "application/json",
            'X-CSRFToken': csrftoken,
        };
        var self=this;
        axios({
            url: window.location.pathname.replace("planner","plannerAPI"),
            data: JSON.stringify({
                'plan_name':planName,
                'bucket_name':bucketName,
                'bucket_id':bucketId,
                'operation_type':"Add",
                'operation': "savePlanBuckets"
            }),
            headers: configHeaders,
            method: "POST",
        })
        .then((res)=>{
            self.props.loadColumn(plan)
        })
        .catch((err) => {
            console.log(err);
         });
    }

    render(){
        return(
            <React.Fragment>
            <div className="card" id="plans_details">
                <div className="card-header shadow" style={{ paddingBottom: "0rem", paddingTop: "0.4rem", border: "solid 1px" }}>
                    <div className="row">
                        <h3 className="col-sm-8" style={{ color: "var(--primary-color)", marginLeft: "2rem" }} id="plan_title">{this.props.plan.plan_name}</h3>
                        <div className="col-sm-2" />
                        <button className="col-sm-1" style={{ background: "black", color: "white", textAlign: "center", padding: "0.2rem", marginTop: "0.2rem", }} id="plan_access_type">{this.props.plan.plan_access} Group</button>
                    </div>
                </div>
                <div className="card-body" style={{ background: "#00000010" }}>
                    <div className="row" id="plan_body">
                        <div className="card col-sm-7" id="plan_details" style={{ border: "solid 0.5px black", height: "2rem", padding: "0.3rem", }} >{this.props.plan.plan_description}</div>
                        <div className="col-sm-1" />
                        <div className="col-sm-1 dropdown">
                            {/* {this.props.plan.plan_access=="Private"?(
                                <React.Fragment> */}
                                    <button id="plan_members" type="button" className="btn btn-primary dropdown-toggle" data-toggle="dropdown" >
                                        <i className="fas fa-user-friends" />&nbsp;Members
                                    </button>
                                    <div className="collapse dropdown-menu" style={{width: "20rem",fontSize: "0.8rem",height: "fit-content",overflow: "unset", }} >
                                        <div className="card">
                                            <div className="card-header">
                                                <h4 className="card-title">Members</h4>
                                            </div>
                                            <div className="card-body" style={{ overflow: "auto", padding: "0.5rem" }} >
                                                <div id="members" style={{ maxHeight: "10rem" }}>
                                                    {this.props.plan.plan_members!=null?
                                                        (this.props.plan.plan_members.map((user)=>{
                                                            return(
                                                                <div className="external-event members_list" style={{position:"relative",color:"var(--primary-color)"}}><b class="img-circle elevation-2" style={{fontSize:"110%",color:"white",borderRadius:"20%",backgroundColor:"black",marginTop:"-0.5em",padding:"0.3em"}}>{user[0].toUpperCase()}</b>&nbsp;&nbsp;<span>{user}</span></div>
                                                            )
                                                        }))
                                                        :
                                                        ('')
                                                    }
                                                </div>
                                            </div>
                                        </div>
                                        <div className="card">
                                            <div className="card-header">
                                                <h3 className="card-title">Add member</h3>
                                            </div>
                                            <div className="form-group" style={{ padding: "0.5rem" }}>
                                                <select id="new-member" className="form-control" multiple>
                                                    {this.props.users.map((user)=>{
                                                        return(
                                                            <React.Fragment>
                                                                <option value={user}>{user}</option>
                                                            </React.Fragment>
                                                        )
                                                    })}
                                                </select>
                                                <br />
                                                <button id="add_new_member" type="button" className="btn btn-primary">
                                                    Add
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                {/* </React.Fragment>
                            ):(
                                ''
                            )} */}
                        </div>
                        <div className="col-sm-1 dropdown" id="add_labels">
                            <button type="button" className="btn btn-primary dropdown-toggle" id="allLabels" data-toggle="dropdown" >
                                <i className="fas fa-tags" />&nbsp;Add labels
                            </button>
                            <div className="dropdown-menu" style={{ height: "fit-content"}} >
                                <div className="card dropdown-item" style={{ background: "white" }}>
                                    <div style={{padding:"0.5rem"}}>
                                        <h4 className="card-title">Labels</h4>
                                    </div>
                                    <div className="card-body" style={{ overflow: "auto", padding: "0.5rem" }} >
                                        <div id="labels" style={{ maxHeight: "10rem" }}></div>
                                    </div>
                                    <div style={{padding:"0.5rem"}}>
                                        <h3 className="card-title">Add label</h3>
                                    </div>
                                    <div className="card-body" style={{ padding: "0.5rem" }}>
                                        <input type="color" style={{margin:"0 0 10px"}} defaultValue="#B8860B" id="label_bg_color" />
                                        <div className="mt-1 mb-1">
                                            <input type="text" id="label_name" className="col-sm-12" style={{ padding: 0 }} placeholder="Label name" maxLength={20} aria-describedby="labelName"/>
                                            <small id="labelName" className="form-text text-muted">
                                                Label name should not contain more than 20 characters.
                                            </small>
                                        </div>
                                        <button id="add_new_label" type="button" className="btn btn-primary">
                                            Add
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="col-sm-1" id="add_columns">
                            <button type="button" className="btn btn-primary" id="addColumns" onClick={()=>{this.addColumn(this.props.plan)}}>
                                <i className="fa fa-plus" />&nbsp;Columns
                            </button>
                        </div>
                        <div className="col-sm-1" id="plan_boards">
                            <button type="button" className="btn btn-primary" id="allPlan">
                                <i className="fas fa-clipboard-list" />&nbsp;All plans
                            </button>
                        </div>
                    </div>
                    <hr style={{ color: "lightgray", border: "solid 1px" }} />
                    <br />
                    <div className="row" id="plan_columns">
                        {this.props.columns?.map((plan_column)=>{
                            return(
                                <React.Fragment>
                                    <PlanColumn bucket_id={plan_column.bucket_id} bucket_name={plan_column.bucket_name} users={this.props.users} plan={this.props.plan} plan_name={this.props.plan.plan_name} tasks={this.props.tasks} loadTasks={()=>{this.props.loadColumn(this.props.plan)}} />
                                </React.Fragment>
                            )
                        })}
                    </div>
                </div>
            </div>
        </React.Fragment>
        )
    }
}

export default PlanDetails;
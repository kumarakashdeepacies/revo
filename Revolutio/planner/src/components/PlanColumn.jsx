import * as React from "react";
import axios from "axios"
import Swal from 'sweetalert2'

class PlanColumn extends React.Component{
    constructor(props){
        super(props);
        this.state={
            assignedUsers:[],
            assignedLabels:[],
        }
    }

    addAssignedUser=(user)=>{
        var assignedUser=this.state.assignedUsers;
        assignedUser.push(user);
        this.setState({
            assignedUsers:assignedUser
        })
    }

    removeAssignedUser=(user)=>{
        var assignedUser=this.state.assignedUsers;
        assignedUser.pop(user);
        this.setState({
            assignedUsers:assignedUser
        })
    }

    removeColumn=(bucketId, bucketName, planName)=>{
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
                'operation_type':"Delete",
                'operation': 'savePlanBuckets'
            }),
            headers: configHeaders,
            method: "POST",
        })
        .then((res)=>{


        })
    }

    addtask=(bucket_id)=>{
        var planName=this.props.plan_name;
        var operation="create";
        var taskId = ("Task"+Math.random()).replace(".","")
        var taskName=document.getElementById('task_name').value;
        var bucketName = document.getElementById('bucketNameParent').value;
        var dueDate = document.getElementById('task_due_date').value;
        var taskDescription = document.getElementById('task_description').value;
        var progress = document.getElementById('progress').value;
        var priority = document.getElementById('priority').value;
        var assignedUsers=this.state.assignedUsers;
        var assignedLabels=this.state.assignedLabels;
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
                'task_name':taskName,
                'task_id':taskId,
                'plan_name':planName,
                'bucket_name':bucketName,
                'bucket_id':bucket_id,
                'due_date':dueDate,
                'task_description':taskDescription,
                'progress':progress,
                'priority':priority,
                'assigned_users':JSON.stringify(assignedUsers),
                'assigned_labels':JSON.stringify(assignedLabels),
                'operation_type':operation,
                'operation': 'saveTask'
            }),
            headers: configHeaders,
            method: "POST",
        })
        .then((res)=>{
            Swal.fire({icon: 'success',text: 'Created successfully!'});
            self.props.loadTasks(self.props.plan);
        })
        .catch((err) => {
            console.log(err);
        });
    }

    render(){
        return(
            <React.Fragment>
                <div className="col-sm-3">
                    <div className="card card-row card-secondary" id={this.props.bucket_id} data-plan_name={this.props.plan_name}>
                        <div className="card-header">
                            <h3 className="card-title contentEditable" data-bucket_id={this.props.bucket_id} data-plan_name={this.props.plan_name}>
                                {this.props.bucket_name}
                            </h3>
                            <div className="card-tools">
                                <button type="button" className="btn btn-tool removeCard" onClick={()=>{this.removeColumn(this.props.bucket_id,this.props.bucket_name,this.props.plan_name)}} data-card-widget="remove"><i class="fas fa-times"></i></button>
                            </div>
                        </div>
                        <div class="card-body task_list" style={{border:"1px solid var(--primary-color)",cursor:"pointer"}}>
                            <button type="button" data-toggle="modal" data-target={"#taskModals"+this.props.bucket_id} class="btn btn-light w-100 addTasks" style={{"textAlign":"left","fontSize":"larger"}} data-bucket_name={this.props.bucket_name} data-bucket_id={this.props.bucket_id}>
                                <i class="fa fa-plus"></i>&nbsp;Add task
                            </button>
                            <div class="modal" tabindex="-1" role="dialog" id={"taskModals"+this.props.bucket_id} name={this.props.bucket_id}>
                        <div class="modal-dialog modal-xl" role="document">
                            <div class="modal-content">
                                <div class="modal-header" style={{background:"#565a5e"}}>
                                    <h5 class="modal-title" style={{color:"white"}}>New Task</h5>
                                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                        <span aria-hidden="true">&times;</span>
                                    </button>
                                </div>
                                <div class="modal-body" style={{maxHeight:"35rem",overflowY:"inherit"}}>
                                    <div class="row">
                                        <div class="col-sm-5">
                                        <div class="form-group" style={{marginLeft: "0.7rem",marginTop: "0.5rem"}}>
                                            <input type="text" id="task_name" class="col-sm-12" style={{padding:"0"}} placeholder="Task name" aria-describedby="taskName" />
                                        </div>
                                        <br />
                                        <input type={"hidden"} value={this.props.bucket_id}/>
                                        <div class="form-group" style={{marginLeft: "0.7rem"}}>
                                            <label>Bucket Name</label>
                                            <input type="text" id="bucketNameParent" class="col-sm-12" style={{padding:"0"}} placeholder="Bucket Name" aria-describedby="bucketName" required />
                                        </div>
                                        <br />
                                        <div class="form-group" style={{marginLeft: "0.7rem"}}>
                                            <label>Set due date</label>
                                            <input type="date" id="task_due_date" class="col-sm-12" />
                                        </div>
                                        <br />
                                        <div class="form-group">
                                            <textarea id="task_description" class="form-control" style={{height:"15rem",maxHeight:"16rem",overflow:"auto",marginLeft:"0.7rem",width:"98%",border:"1px solid var(--primary-color)",padding:"1rem"}} placeholder="Task description"></textarea>
                                        </div>
                                        </div>
                                        <div class="col-sm-1"></div>
                                        <div class="col-sm-6">
                                        <div class="form-group" style={{marginLeft: "0.2rem"}}>
                                            <label>Progress status</label>
                                            <select id="progress" class="form-control select2">
                                            <option value="Not started">Not started</option>
                                            <option value="In progress">In progress</option>
                                            <option value="Complete">Complete</option>
                                            </select>
                                        </div>
                                        <div class="form-group" style={{marginLeft: "0.2rem"}}>
                                            <label>Priority status</label>
                                            <select id="priority" class="form-control select2">
                                            <option value="High">High</option>
                                            <option value="Medium">Medium</option>
                                            <option value="Low">Low</option>
                                            </select>
                                        </div>
                                        <div class="form-group" style={{marginLeft: "0.2rem"}}>
                                                {this.state.assignedUsers.map((user)=>{
                                                    return(
                                                        <div class="card" id="assigned_users" style={{maxHeight: "10rem",overflow: "hidden",border: "solid 0.1em var(--primary-color)", padding:"10px"}}>
                                                            <div class="row" style={{padding:"10px"}}>
                                                                <div class="col-sm-11">
                                                                    <b class="img-circle elevation-2" style={{color:"white",borderRadius:"20%",backgroundColor:"black",marginTop:"-0.5em",padding:"0.3em"}}>
                                                                        {user[0].toUpperCase()}
                                                                    </b>
                                                                    &nbsp;&nbsp;
                                                                    <span>{user}</span>
                                                                </div>
                                                                <div class="col-sm-1">
                                                                    <span class="badge">
                                                                        <i class="fa fa-times deleteUser" onClick={()=>{this.removeAssignedUser(user)}} style={{fontSize:"0.9rem",color:"gray"}}></i>
                                                                    </span>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    )
                                                })}
                                            <div class="dropdown">
                                                <button class="btn btn-primary dropdown-toggle" type="button" data-toggle="dropdown">
                                                    <i class='fas fa-user-plus'></i>&nbsp;Assign users
                                                </button>
                                                <ul class="dropdown-menu" id="assign_users" style={{maxHeight:"700px",overflow:"scroll"}}>
                                                    {this.props.users.map((user)=>{
                                                        if(!this.state.assignedUsers.includes(user)){
                                                            return(
                                                                <React.Fragment>
                                                                    <li class="list-group-item members_list assign" onClick={()=>{this.addAssignedUser(user)}} style={{position: "relative",color:"var(--primary-color)",cursor:"pointer",padding:"0.8rem"}}><b class="img-circle elevation-2" style={{color:"white",borderRadius:"20%",backgroundColor:"black",marginTop:"-0.5em",padding:"0.3em"}} onClick={this.addAssignedUser}><img />{user[0].toUpperCase()}</b>&nbsp;&nbsp;<span>{user}</span></li>
                                                                </React.Fragment>
                                                            )
                                                        }
                                                    })}
                                                </ul>
                                            </div>
                                        </div>
                                        <div class="form-group" style={{marginLeft: "0.2rem"}}>
                                            <div class="card" style={{paddingTop: "0.5rem",maxHeight: "5rem",overflow: "auto",border: "0.1em solid var(--primary-color)",display: "none"}}>
                                            <div class="row" id="assigned_labels" style={{marginRight:"0"}}></div>
                                            </div>
                                            <div class="dropdown">
                                            <button class="btn btn-primary dropdown-toggle" type="button" data-toggle="dropdown">
                                                <i class="fas fa-tags"></i>&nbsp;Add labels
                                            </button>
                                            <ul class="dropdown-menu">
                                                <div class="row" id="assign_labels" style={{marginRight:"0"}}></div>
                                            </ul>
                                            </div>
                                        </div>

                                        </div>
                                    </div>
                                </div>
                                <div class="modal-footer" style={{paddingTop:"0.5rem",paddingBottom:"0.5rem"}}>
                                    <button type="button" onClick={()=>{this.addtask(this.props.bucket_id)}} class="btn btn-primary" id="saveTask" data-dismiss="modal" aria-label="Close">Save</button>
                                </div>
                            </div>
                        </div>
                    </div>
                            {this.props.tasks.map((task)=>{
                                if(task.task_overdue=="Yes"){
                                  var span_display = "block";
                                  var span_text = task.task_overdue_days + " day/days overdue.";
                                  var background = "#ff000050"
                                }
                                else{
                                  var span_display = "none";
                                  var span_text = '';
                                  var background = ''
                                }
                                if(task.task_members.length>5){
                                  var icon_display = 'block';
                                }
                                else{
                                  var icon_display = 'none';
                                }
                                if(task.bucket_id==this.props.bucket_id){
                                    return(
                                        <React.Fragment>
                                            <div class="card bucket_tasks shadow" id={task.task_id} data-bucket_name={task.bucket_name} data-bucket_id={task.bucket_id} data-task_name={task.task_name} data-due_date={task.due_date} data-task_description={task.task_description} data-progress={task.progress_status} data-priority={task.priority_status} data-assigned_users={task.task_members} data-assigned_labels={task.task_labels} style={{cursor: "pointer"}}>
                                                <div class="card-header pb-0" style={{color:"var(--primary-color)",paddingTop:"0.7rem"}}><h5>{task.task_name}</h5></div>
                                                <div class="card-body">
                                                    <div class="row">
                                                        <div class="col-sm-4 card" style={{fontWeight:"bold"}}>{task.progress_status}</div>
                                                        <div class="col-sm-4 card" style={{fontWeight:"bold"}}>{task.priority_status}</div>
                                                        <div class="col-sm-4 card" style={{fontWeight:"bold",background:background}}>{task.due_date}</div>
                                                    </div>
                                                    <div class="row" style={{"display":span_display}}><span style={{color:"red"}}>{span_text}</span></div>
                                                    <br />
                                                    <div class="row">

                                                    </div>
                                                </div>
                                                <div class="card-footer">
                                                    <div class="row">
                                                        <div class="icon" style={{marginTop:"0.5rem",marginLeft:"1rem",display:{icon_display}}}><i class="fa fa-plus"></i></div>
                                                    </div>
                                                </div>
                                            </div>
                                        </React.Fragment>
                                    )
                                }
                            })}
                        </div>
                    </div>
                </div>
            </React.Fragment>
        )
    }
}

export default PlanColumn;
import * as React from "react";
import PlanDetails from "./PlanDetails";
import Plans from "./Plans";
import axios from "axios";
import Swal from "sweetalert2"

class Body extends React.Component{
    constructor(props){
        super(props);
        this.state={
            plans:[],
            users:[],
            columns:[],
            tasks:[],
            isActivePlan:false,
            activePlan:{},
            newPlanName:'',
            newPlanAccess:'',
            newPlanDescription:''
        }
    }

    createNewPlan=()=>{
      var planName=document.getElementById('plan_name').value;
      var planAccess=document.querySelector('input[name="plan_type"]:checked').value;
      var planDesc=document.getElementById('plan_description').value;
      if(planAccess==''){
        return;
      }
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
              'plan_access':planAccess,
              "plan_description":planDesc,
              'operation': "savePlan"
          }),
          headers: configHeaders,
          method: "POST",
      })
      .then((response)=>{
        Swal.fire({icon: 'success',text: 'Created successfully!'});
        var newPlan={};
        newPlan["plan_name"]=planName;
        newPlan["plan_access"]=planAccess;
        newPlan["plan_description"]=planDesc;
        newPlan["plan_id"]=planName.replace(/\s/g, "");
        newPlan["plan_members"]=null;
        newPlan["plan_labels"]=null;
        self.addNewPlan(newPlan);
      })
      .catch((err) => {
          console.log(err);
       });
    }

    addNewPlan=(new_plan)=>{
      var newPlan=new_plan;
      var oldPlans=this.state.plans;
      oldPlans.push(newPlan);
      this.setState({
        plans:oldPlans
      });
    }

    getPlansAndUsers=()=>{
      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value
      const configHeaders = {
          "content-type": "application/json",
          "Accept": "application/json",
          'X-CSRFToken': csrftoken,
      };
      var self=this;
      axios({
        url: window.location.pathname.replace("planner","plannerAPI"),
        headers: configHeaders,
        method: "GET",
      })
      .then((res)=>{
        self.setState({
          users:res.data.users,
          plans:res.data.plans
        })
      })
      .catch((err) => {
          console.log(err);
      });
    }

    componentDidMount=()=>{
      this.getPlansAndUsers();
    }

    loadColumns=(plan)=>{
      var planName = plan.plan_name;
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
              'operation': "loadPlanColumns"
          }),
          headers: configHeaders,
          method: "POST",
      })
      .then((res)=>{
        self.setState({
          columns:res.data.plan_columns,
          tasks:res.data.plan_tasks
        },()=>{this.appendColumns()})
      })
      .catch((err) => {
          console.log(err);
       });
    }

    appendColumns=()=>{
      var columns=this.state.columns;
    }

    changeValues=(e)=>{
      var target=e.target;
      if(target.id=="plan_name"){
        this.setState({
          newPlanName:target.value
        })
      }
      if(target.id=="plan_description"){
        this.setState({
          newPlanDescription:target.value
        })
      }
    }

    render(){
        return (
            <div className="App">
              <div className="container-fluid" style={{"padding":0}}>
                <div className="card" id="plans_board_main">
                  <div className="card-header shadow" style={{"paddingBottom":"0rem", "paddingTop":"0.4rem", "border":"solid 1px"}}>
                    <h3 style={{"color":"var(--primary-color)","textAlign":"center"}}>Plans</h3>
                  </div>
                </div>
              </div>
              <div className="card-body" style={{"background":"#00000010"}}>
                <div className="row" id="plans">
                  <div className="small-box col-sm-3" data-toggle="modal" data-target="#planModal" style={{"cursor":"pointer","background":"whitesmoke","height":"7rem","marginLeft":"2rem"}} id={"addPlan "}>
                    <div className="inner">
                      <h4 style={{"marginTop":"2rem"}}>New Plan</h4>
                    </div>
                    <div className="icon">
                      <i className="fa fa-plus" style={{"fontSize":"3rem","marginTop":"1rem"}}></i>
                    </div>
                  </div>
                  {this.state.plans.map((plan)=>{
                    return(
                      <React.Fragment>
                        <Plans plan={plan} setActivePlan={plan=>{this.setState({activePlan:plan,isActivePlan:true});this.loadColumns(plan)}}/>
                      </React.Fragment>
                    )
                  })}
                </div>
              </div>
              {this.state.isActivePlan?(
                <React.Fragment>
                    <PlanDetails plan={this.state.activePlan} columns={this.state.columns} users={this.state.users} loadColumn={()=>{this.loadColumns(this.state.activePlan)}} tasks={this.state.tasks} />
                </React.Fragment>
              ):(
                ''
              )}
              <div class="modal fade" id="planModal" tabindex="-1" role="dialog" aria-labelledby="planLabel" aria-hidden="true">
                <div class="modal-dialog" role="document">
                  <div class="modal-content">
                    <div class="modal-header">
                      <h5 class="modal-title" style={{"color":"var(--primary-color)"}} id="planLabel">New Plan</h5>
                      <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                      </button>
                    </div>
                    <div class="modal-body">
                    <div class="form-group">
                      <input type="text" id="plan_name" class="col-sm-10" style={{"padding":0}} placeholder="Plan name" maxlength="20" aria-describedby="planName" />
                      <small id="planName" class="form-text text-muted">
                        Plan name should not contain more than 20 characters.
                      </small>
                    </div>
                    <br />
                    <br />
                    <div class="custom-control custom-radio ">
                      <input type="radio" id="rd_1" name="plan_type" class="custom-control-input" value="Public" />
                      <label class="custom-control-label black" for="rd_1">Public - Any member of the project can see plan contents</label>
                    </div>
                    <div class="custom-control custom-radio ">
                      <input type="radio" id="rd_2" name="plan_type" class="custom-control-input" value="Private" />
                      <label class="custom-control-label black" for="rd_2">Private - Only members I add can see plan contents</label>
                    </div>
                  <br />
                  <div class="form-group">
                    <textarea id="plan_description" class="form-control" style={{"height":"8rem","maxHeight":"15rem","overflow":"auto","marginLeft":"0.7rem","border":"1px solid darkgolderod","padding":"1rem"}} placeholder="Plan description"></textarea>
                  </div>
                    </div>
                    <div class="modal-footer">
                      <button type="button" class="btn btn-primary" onClick={this.createNewPlan} data-dismiss="modal" aria-label="Close">Create Plan</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
    }
}

export default Body;
import * as React from "react";

class Plans extends React.Component{
    constructor(props){
        super(props);
    }
    render(){
        return(
            <React.Fragment>
              <div class="small-box col-sm-3 plans_boards" onClick={()=>{this.props.setActivePlan(this.props.plan)}} id={this.props.plan.plan_id} style={{"border":"2px solid var(--primary-color)","height":"7rem","background":"white","marginLeft":"2rem","cursor":"pointer"}} data-plan_name={this.props.plan.plan_name} data-plan_description={this.props.plan.plan_description} data-plan_access={this.props.plan.plan_access} data-plan_members={this.props.plan.plan_members} data-plan_labels={this.props.plan.plan_labels}>
                <div class="inner">
                  <h4 style={{"marginTop":"2rem","color":"#565a5e"}}>{this.props.plan.plan_name}</h4>
                </div>
                <div class="icon">
                  <i class="fa fa-tasks" style={{"fontSize":"3rem","color":"black","marginTop":"1rem"}}></i>
                </div>
              </div>
            </React.Fragment>
        )
    }
}

export default Plans;
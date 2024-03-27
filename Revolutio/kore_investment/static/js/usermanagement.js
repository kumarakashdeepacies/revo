/* eslint camelcase: ["error", {ignoreGlobals: true,properties:'never'}] */
/* eslint valid-typeof: ["error", { "requireStringLiterals": true }] */

// Server-side rendering of User table
function renderUserTables() {
  const userColumnArray = [
    {
      data: "username",
      title: "Name",
      render: function (data, type, row, meta) {
        if (type == "display") {
          let userString = '<div class="img-circle elevation-2 navlink-img">';
          if (row.profile_pic) {
            userString += `<img src="/media/${row.profile_pic}" class="img-circle elevation-2 mx-auto user-profile-photo"
            alt="User profile picture">`;
          } else if (row.first_name) {
            userString += `<b class="profile-initials">${row.first_name[0]}${row.last_name[0]}</b>`;
          } else {
            userString += `<b class="profile-initials">${row.username[0]}</b>`;
          }
          userString += "</div>";
          userString += `
          <div class="username_details">
            <h5 class="col-username">${row.first_name} ${row.last_name}</h5>
            <div class="col-additional-info">${row.username}</div>
          </div>
          `;
          return `<div class="user_details" style="padding-left:1rem;">${userString}</div>`;
        } else {
          return data;
        }
      },
    },
    {
      data: "role",
      title: "Role",
      render: function (data, type, row, meta) {
        if (type === "display") {
          let updatedValue = "";
          if (data == "No Access Assigned") {
            updatedValue =
              '<div class="roles-ui-buttons no-role">Unassigned</div>';
          } else {
            updatedValue = '<div class="roles-ui-buttons role-user">User</div>';
            if (data === "Admin") {
              updatedValue +=
                '<div class="roles-ui-buttons role-admin">Admin</div>';
            } else if (data === "Developer") {
              updatedValue +=
                '<div class="roles-ui-buttons role-developer">Developer</div>';
            } else if (data === "Admin and Developer") {
              updatedValue +=
                '<div class="roles-ui-buttons role-admin">Admin</div>';
              updatedValue +=
                '<div class="roles-ui-buttons role-developer">Developer</div>';
            }
          }
          return `<div class="user_details roles" >${updatedValue}</div>`;
        } else {
          return data;
        }
      },
      searchable: true,
    },
    {
      data: "action",
      title: "Action",
      render: function (data, type, row, meta) {
        if (type == "display") {
          let removeUser = "";
          if (row.role === "No Access Assigned") {
            removeUser = "disabled";
          }
          let actionString = `<div>
          <div class="tab_view_actions user_details">
            <a href="/users/${app_code2}/${current_dev_mode2}/user_management/user_logout/${row.id}/" class="call_to_action_buttons logout-user" data-toggle="tooltip" title="Logout User"> <i class="fas fa-power-off fa-lg"></i> </a>
            <button class="call_to_action_buttons manage-user" data-toggle="modal" data-target="#ManageUserModal" onclick="manageUser('${row.id}','${row.username}','${row.first_name}','${row.last_name}','${row.email}','${row.role}','${row.profile_pic}','${row.first_name[0]}','${row.last_name[0]}')"> <i class="fas fa-user-cog fa-lg mr-2"></i> Manage User </button>
            <button class="call_to_action_buttons remove-user" data-user="${row.username}" data-user-id="${row.id}" ${removeUser} onclick="removeUser.call(this)"> <i class="fa-solid fa-user-xmark fa-lg mr-2"></i> Remove User </button>
            <div class="radioGroup" style="overflow: hidden ;">
          `;
          let active = "checked";
          let activeText = "Active";
          let inactive = "";
          let inactiveText = "Deactivate";
          if (!row.is_active) {
            active = "";
            activeText = "Activate";
            inactive = "checked";
            inactiveText = "Inactive";
          }
          actionString += `
              <input type="radio" id="activate_user_${row.id}" data-user="${row.username}" ${active} data-user-id="${row.id}" class="activate_user" value="activate_user" name="activate_deactivate_${row.id}">
              <label for="activate_user_${row.id}" style="margin-top: 0.8%;margin-bottom: 0;">${activeText}</label>
              <input type="radio" id="deactivate_user_${row.id}" data-user="${row.username}" ${inactive} data-user-id="${row.id}" class="deactivate_user" value="deactivate_user" name="activate_deactivate_${row.id}">
              <label for="deactivate_user_${row.id}" style="margin-top: 0.8%;margin-bottom: 0;">${inactiveText}</label>
              <span class="indicator"></span>
            </div>
          </div>
          <div class="mobile_view_actions">
            <i class="fa-solid fa-gears dropdown-i" data-toggle="dropdown"></i>
            <div class="dropdown-menu dropdown-menu-sm dropdown-menu-right user-actions-dropdown">
                <span class="dropdown-item" data-toggle="modal" data-target="#ManageUserModal" onclick="manageUser('${row.id}','${row.username}','${row.first_name}','${row.last_name}','${row.email}','${row.role}','${row.profile_pic}','${row.first_name[0]}','${row.last_name[0]}')">
                    <i class="fas fa-user-cog fa-lg mr-2"></i> Manage User
                </span>
                <div class="dropdown-divider"></div>
                <span class="dropdown-item" data-user="${row.username}" data-user-id="${row.id}" ${removeUser} onclick="removeUser.call(this)">
                    <i class="fa-solid fa-user-xmark fa-lg mr-2" style="color:red"></i> Remove User
                </span>
                <div class="dropdown-divider"></div>
          `;
          if (row.is_active) {
            actionString += `
                <span class="dropdown-item deactivate_user" data-user="${row.username}">
                    <i class="fa-solid fa-user-minus fa-lg mr-2" style="color:#f91c1c"></i> Deactivate User
                </span>
            `;
          } else {
            actionString += `
                <span class="dropdown-item activate_user" data-user="${row.username}">
                    <i class="fa-solid fa-user-check fa-lg mr-2" style="color:#00e936"></i> Activate User
                </span>
            `;
          }
          actionString += `
                <div class="dropdown-divider"></div>
                  <span class="dropdown-item" onclick='window.location.href="/users/${app_code2}/${current_dev_mode2}/user_management/user_logout/${row.id}/"'>
                      <i class="fa-solid fa-power-off fa-lg mr-2" style="color:#f91c1c"></i> Logout User
                  </span>
              </div>
            </div>
          </div>`;
          return actionString;
        } else {
          return data;
        }
      },
    },
  ];
  var user_table = $(`#userTable`)
    .DataTable({
      scrollY: "50vh",
      scrollCollapse: true,
      scrollX: "120%",
      ordering: false,
      autoWidth: false,
      bAutoWidth: false,
      serverSide: true,
      orderCellsTop: true,
      responsive: true,
      colReorder: {
        fixedColumnsLeft: 1,
      },
      stateSave: false,
      deferRender: true,
      paging: true,
      stripeClasses: [],
      pageLength: 50,
      lengthMenu: [
        [1, 5, 50, 100, -1],
        [1, 5, 50, 100, "All"],
      ],
      dom: "lrtip",
      buttons: [],
      ajax: `/users/${app_code2}/${current_dev_mode2}/user_management/fetch_user_server_side/`,
      columns: userColumnArray,
      columnDefs: [
        {
          targets: "_all",
          className: "dt-center allColumnClass all",
          width: "33%",
        },
      ],
      sScrollX: "120%",
      initComplete: function () {
        $("#userTable_info").css("margin-left", "1rem");
        $("#userTable_paginate").css("margin-right", "1rem");
        $(".activate_user").off("click").on("click", activateUser);
        $(".deactivate_user").off("click").on("click", deactivateUser);
      },
    })
    .columns.adjust();

  $("#searchUsers")
    .off("keyup")
    .on("keyup", function () {
      let searchValue = this.value;
      user_table.columns(0).search(searchValue).draw();
    });

  $("#userTable_wrapper").prepend("<div class='show_filter_wrap'></div>");

  $("#userTable_length").appendTo(".show_filter_wrap");

  role_filter_html = `
    <div id="userTable_role_type_filter" class="datatable_filter_role_type">
        <div class="role_filter_wrap">
            <h6 class="mb-0 mr-2">Filter by Role:</h6>
            <select id="role_type_filter" style="border-radius:1.8rem">
              <option value="">All</option>
              <option value="User">User</option>
              <option value="Developer">Developer</option>
              <option value="Admin">Admin</option>
              <option value="Unassigned">Unassigned</option>
            </select>
        </div>
    </div>
  `;

  $(role_filter_html).appendTo(".show_filter_wrap");

  $("#role_type_filter").select2();

  $("#role_type_filter")
    .off("select2:select")
    .on("select2:select", function () {
      let selectedTerm = this.value;
      user_table.columns(1).search(selectedTerm).draw();
    });

  $("[name=userTable_length]").closest("label").css("display", "flex");
  $("[name=userTable_length]").closest("label").css("align-items", "center");
  $("[name=userTable_length]").closest("label").css("gap", "9px");
  $("[name=userTable_length]").closest("label").css("text-indent", "0");
  $("[name=userTable_length]").closest("label").css("padding-left", "7.5px");
  $("[name=userTable_length]").select2({
    width: "50%",
  });
}

function activateUser() {
  $(this).next("label").text("Active");
  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/user_management/`,
    data: {
      operation: "user_app_activation",
      username: $(this).attr("data-user"),
      is_active: "true",
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      Swal.fire({ icon: "success", text: "User activated successfully!" });
    },
    error: function () {
      Swal.fire({ icon: "error", text: "Error! Please try again." });
    },
  });
}

function deactivateUser() {
  username = $(this).attr("data-user");
  element = $(this);
  Swal.fire({
    icon: "question",
    text: "Are you sure you wish to deactivate " + username + " from the app?",
    showDenyButton: true,
  }).then((result) => {
    if (result.isConfirmed) {
      $(element).next("label").text("Inactive");
      $.ajax({
        url: `/users/${app_code2}/${current_dev_mode2}/user_management/`,
        data: {
          operation: "user_app_activation",
          username: username,
          is_active: "false",
        },
        type: "POST",
        dataType: "json",
        success: function (data) {
          Swal.fire({
            icon: "success",
            text: "User deactivated successfully!",
          });
        },
        error: function () {
          Swal.fire({ icon: "error", text: "Error! Please try again." });
        },
      });
    } else {
      $(element)
        .closest(".radioGroup")
        .find(".activate_user")
        .prop("checked", true)
        .trigger("change");
    }
  });
}

function level_0_selected() {
  if ($("#id_permission_level").val() == "0") {
    var permission_value = $("#id_permission_name").val();
    var permission_name = $(
      `#id_permission_name option[value='${permission_value[0]}']`
    ).html();
  }
  $(`#newdiv button[value='${permission_value}']`).on("click", functionbutton);

  if ($("#id_permission_level").val() != "0") {
    var level_0_perm_selected = $("#id_permission_name").val();
    $.ajax({
      url: `/users/${app_code2}/${current_dev_mode2}/user_management/`,

      data: {
        operation: "level_0_selected",
        selected: JSON.stringify(level_0_perm_selected),
        app_code: $("#id_application").val(),
      },
      type: "POST",
      dataType: "json",
      success: function (data) {
        var store_previous_level1_values = [];
        var cascading = false;
        $("#div_level_1").css("display", "block");
        if ($("#id_level_1").val().length > 0) {
          store_previous_level1_values = $("#id_level_1").val();
          cascading = true;
        }
        var valPresent = [];
        $("#div_level_1")
          .find("button[type=button]")
          .each(function () {
            valPresent.push($(this).attr("value"));
          });
        $("#id_level_1").empty();
        for (var i = 0; i < data.data.length; i++) {
          if (!valPresent.includes(data.data[i].item_code)) {
            if (store_previous_level1_values.includes(data.data[i].item_code)) {
              $("#id_level_1").append(
                new Option(
                  data.data[i].item_name,
                  data.data[i].item_code,
                  false,
                  true
                )
              );
            } else {
              $("#id_level_1").append(
                new Option(
                  data.data[i].item_name,
                  data.data[i].item_code,
                  false,
                  false
                )
              );
            }
          }
        }
        if (cascading) {
          level_1_selected();
        }
      },
      error: function () {
        Swal.fire({
          icon: "error",
          text: "Error! Failure in assigning Level 1 permission. Please try again",
        });
      },
    });
  }
}

function hierarchy_selected() {
  var level_0_perm_selected = $("#id_permission_name").val();
  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/user_management/`,

    data: {
      operation: "hierarchy_selected",
      selected: JSON.stringify(level_0_perm_selected),
      app_code: $("#id_application").val(),
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      var store_previous_level1_values = [];
      $("#div_level_1").css("display", "block");
      if ($("#id_level_1").val().length > 0) {
        store_previous_level1_values = $("#id_level_1").val();
      }
      $("#id_level_1").empty();
      for (var i = 0; i < data.data.length; i++) {
        if (
          store_previous_level1_values.includes(data.data[i].hierarchy_name)
        ) {
          $("#id_level_1").append(
            new Option(
              data.data[i].hierarchy_name,
              data.data[i].Hierarchy_concat,
              false,
              true
            )
          );
        } else {
          $("#id_level_1").append(
            new Option(
              data.data[i].hierarchy_name,
              data.data[i].Hierarchy_concat,
              false,
              false
            )
          );
        }
      }
    },
    error: function () {
      Swal.fire({
        icon: "error",
        text: "Error! Failure in assigning Level 1 permission. Please try again",
      });
    },
  });
}

function functionbutton(e) {
  $(`<option value='${e.target.value}'> ${e.target.name}</option>`).appendTo(
    "#id_permission_name"
  );
  $(this).remove();
}

function level_1_selected() {
  if ($("#id_permission_level").val() == "1") {
    var permission_value = $("#id_level_1").val();
    var permission_name = $(
      `#id_level_1 option[value='${permission_value[0]}']`
    ).html();
  }
  if ($("#id_permission_level").val() != "1") {
    var level_1_perm_selected = $("#id_level_1").val();
    $.ajax({
      url: `/users/${app_code2}/${current_dev_mode2}/user_management/`,

      data: {
        operation: "level_1_selected",
        selected: JSON.stringify(level_1_perm_selected),
        app_code: $("#id_application").val(),
      },
      type: "POST",
      dataType: "json",
      success: function (data) {
        var store_previous_level2_values = [];
        var cascading = false;
        $("#div_level_2").css("display", "block");
        if ($("#id_level_2").val().length > 0) {
          store_previous_level2_values = $("#id_level_2").val();
          cascading = true;
        }
        $("#id_level_2").empty();
        var valPresent = [];
        $("#div_id_level_2")
          .find("button[type=button]")
          .each(function () {
            valPresent.push($(this).attr("value"));
          });
        for (var i = 0; i < data.data.length; i++) {
          if (!valPresent.includes(data.data[i].tab_type)) {
            if (store_previous_level2_values.includes(data.data[i].tab_type)) {
              $("#id_level_2").append(
                new Option(
                  data.data[i].tab_header_name,
                  data.data[i].tab_type,
                  false,
                  true
                )
              );
            } else {
              $("#id_level_2").append(
                new Option(
                  data.data[i].tab_header_name,
                  data.data[i].tab_type,
                  false,
                  false
                )
              );
            }
          }
        }
        if (cascading) {
          //   level_2_selected()
        }
      },
      error: function () {
        Swal.fire({
          icon: "error",
          text: "Error! Failure in assigning Level 2 permission. Please try again",
        });
      },
    });
  }
}

function functionbtn(e) {
  if ($(this).attr("data-parent") == $("#id_permission_name").val()) {
    $(`<option value='${e.target.value}'> ${e.target.name}</option>`).appendTo(
      "#id_level_1"
    );
  }
  $(this).remove();
}

function addBtnPerm() {
  $("#id_level_button_access").empty();
  let permButtonList = [
    "CreateView - Save",
    "CreateView - Save as Draft",
    "CreateView - Back",
    "CreateView - Custom Validation",
    "CreateView - Refresh Computation",
    "CreateView - View History",
    "CreateView - View Rejected Records",
    "CreateView - View Transaction Status",
    "CreateView - Approval Parameters",
    "CreateView - Reset Draft Status",
    "UploadView - Upload",
    "UploadView - Map Columns",
    "UploadView - Custom Validation",
    "UploadView - Add computation logic",
    "UploadView - Download data",
    "UploadView - Upload history",
    "UploadView - Last upload errors",
    "UploadView - Detailed error log",
    "UploadView - Transaction status",
    "UploadView - SFTP connectors",
    "ListView - Save template",
    "ListView - Upload",
    "ListView - Paste Tabular Data",
    "ListView - Edit Mode",
    "ListView - Delete all data",
    "ListView - Find and replace",
    "ListView - Freeze Panes",
    "ListView - Formatters",
    "ListView - Transactions Status",
    "ListView - Plot Charts",
    "ListView - Filter",
    "ListView - Add Computed Fields",
    "ListView - Expand",
    "ListView - Edit Record",
    "ListView - Delete Record",
    "ListView - View Record",
    "ListView - Extract Data",
    "ListView - Bulk Update",
    "ListView - Conditional Delete",
    "ListView - Approve all",
    "ListView - Reject all",
    "ListView - Approve Multiple",
    "ListView - Reject Multiple",
    "Computation - Run Model",
    "Computation - Configure Scenario",
    "Computation - Filter",
    "Analysis - Previous Versions",
    "Analysis - Save and Share",
    "Analysis - Plot charts",
    "Analysis - Global Settings",
    "Analysis - PDF",
    "Analysis - Save",
    "Analysis - Add tab",
    "Analysis - Tab config",
    "Analysis - Import dashboard",
    "Analysis - Publish",
  ];

  let tpermButtonList = [];
  $("#div_id_level_2 button").each(function () {
    var btnvalue1 = $(this).attr("value").split("__")[1];
    if (btnvalue1 == "create_view") {
      tpermButtonList = tpermButtonList.concat(
        permButtonList.filter((ipermButton) =>
          ipermButton.startsWith("CreateView")
        )
      );
    }
    if (btnvalue1 == "list_view") {
      tpermButtonList = tpermButtonList.concat(
        permButtonList.filter((ipermButton) =>
          ipermButton.startsWith("ListView")
        )
      );
    }
    if (btnvalue1 == "data_connector") {
      tpermButtonList = tpermButtonList.concat(
        permButtonList.filter((ipermButton) =>
          ipermButton.startsWith("UploadView")
        )
      );
    }
    if (btnvalue1 == "computation") {
      tpermButtonList = tpermButtonList.concat(
        permButtonList.filter((ipermButton) =>
          ipermButton.startsWith("Computation")
        )
      );
    }
    if (btnvalue1 == "analysis") {
      tpermButtonList = tpermButtonList.concat(
        permButtonList.filter((ipermButton) =>
          ipermButton.startsWith("Analysis")
        )
      );
    }
  });
  for (i in tpermButtonList) {
    if (
      $(`#id_level_button_access option[value='${tpermButtonList[i]}']`)
        .length != 1
    ) {
      $("#id_level_button_access").append(
        $("<option></option>")
          .attr("value", tpermButtonList[i])
          .text(tpermButtonList[i])
      );
    }
  }
}

function level_2_selected(e) {
  $("#div_id_level_2").find("button").remove();

  var permission_value = $("#id_level_2").val();

  for (let i = 0; i < permission_value.length; i++) {
    var permission_name = $(
      `#id_level_2 option[value='${permission_value[i]}']`
    ).html();
    if (permission_name != undefined) {
      $(`<button style="display:none" type='button' class='btn btn-dark m-1' name='${permission_name}'
                                  value='${permission_value}' data-parent="${$(
        "#id_level_1"
      ).val()}"> ${permission_name}</button>`).appendTo("#div_id_level_2");
      $(`#div_id_level_2 button[value='${permission_value}']`).on(
        "click",
        functionbutton2
      );
    }
  }
  addBtnPerm();
}

function functionbutton2(e) {
  if ($(this).attr("data-parent") == $("#id_level_1").val()) {
    $(`<option value='${e.target.value}'> ${e.target.name}</option>`).appendTo(
      "#id_level_2"
    );
  }
  $(this).remove();
  addBtnPerm();
}

function deleteUserGroup(id, groupName) {
  url = `users/${app_code2}/${current_dev_mode2}/user_management/`;

  Swal.fire({
    icon: "question",
    text: `Are you sure you want to delete ${groupName} group?`,
    showDenyButton: true,
    showCancelButton: false,
    confirmButtonText: "Yes",
    denyButtonText: `No`,
    showCloseButton: true,
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
        url: `/users/${app_code2}/${current_dev_mode2}/user_management/`,
        data: {
          operation: "deleteUserGroupObj",
          group_name: groupName,
          group_id: id,
        },
        dataType: "json",
        type: "POST",
        success: function (d) {
          Swal.fire({ icon: "success", text: d.response }).then((result) => {
            if (result.isConfirmed) {
              window.location.reload();
            }
          });
        },
        error: function () {
          Swal.fire({ icon: "error", text: "Error! Please try again" });
        },
      });
    }
  });
}

function editUserGroupName(id, groupName) {
  $("#edit_group_input").val(groupName);
  $("#edit_group_input").attr("data-groupId", id);
  $("#edit_group_input").attr("data-oldname", groupName);
  $("#edit_group").modal("show");
}

function renameUserGroup() {
  var group_id = $("#edit_group_input").attr("data-groupId");
  var old_groupname = $("#edit_group_input").attr("data-oldname");
  var new_groupname = $("#edit_group_input").val();

  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/user_management/`,
    data: {
      operation: "renameUserGroup",
      old_group_name: old_groupname,
      new_group_name: new_groupname,
      group_id: group_id,
    },
    dataType: "json",
    type: "POST",
    success: function (d) {
      Swal.fire({ icon: "success", text: "" }).then((result) => {
        if (result.isConfirmed) {
          window.location.reload();
        }
      });
    },
    error: function () {
      Swal.fire({ icon: "error", text: "Error! Please try again" });
    },
  });
}

function removeUserFromGroup() {
  var groupName = $(this).attr("data-group-name");
  var userName = $(this).attr("data-username");

  Swal.fire({
    icon: "question",
    text: `Are you sure you want to remove ${userName} user from ${groupName} group?`,
    showDenyButton: true,
    showCancelButton: false,
    confirmButtonText: "Yes",
    denyButtonText: `No`,
    showCloseButton: true,
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
        url: `/users/${app_code2}/${current_dev_mode2}/user_management/`,
        data: {
          operation: "deleteUserFromGroup",
          group_name: groupName,
          user_name: userName,
        },
        dataType: "json",
        type: "POST",
        success: function (d) {
          window.location.reload();
        },
        error: function () {
          Swal.fire({ icon: "error", text: "Error! Please try again" });
        },
      });
    } else if (result.isDenied) {
    }
  });
}

function removeUser() {
  var username = $(this).attr("data-user");
  var user_id = $(this).attr("data-user-id");

  Swal.fire({
    icon: "question",
    text: `Are you sure you wish to remove ${username} from the app? This will remove the user from all the groups with permissions for this app.`,
    showDenyButton: true,
    showCancelButton: false,
    confirmButtonText: "Yes",
    denyButtonText: `No`,
    showCloseButton: true,
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
        url: `/users/${app_code2}/${current_dev_mode2}/user_management/`,
        data: {
          user_id: user_id,
          operation: "remove_user_from_app",
        },
        dataType: "json",
        type: "POST",
        success: function (d) {
          Swal.fire({
            icon: "success",
            text: "User removed from the app successfully.",
          });
          $(`#userTable`).DataTable().draw();
        },
        error: function () {
          Swal.fire({ icon: "error", text: "Error! Please try again" });
        },
      });
    } else if (result.isDenied) {
    }
  });
}

function restrictFile(uploadField) {
  var file = document.getElementById(uploadField);
  if (file.value) {
    var fileName = file.value;
    idxDot = fileName.lastIndexOf(".") + 1;
    extFile = fileName.substr(idxDot, fileName.length).toLowerCase();
    if (extFile != "csv" && extFile != "xlsx") {
      Swal.fire({
        text: "Only csv and xlsx files are allowed!",
        icon: "warning",
      }).then((result) => {
        if (result.isConfirmed) {
          file.value = "";
          $(file).siblings(".custom-file-label").html("Upload File");
        }
      });
    } else {
      $(`#${uploadField}`)
        .closest("form")
        .find("button[type=submit]")
        .prop("disabled", false);
    }
  }
}

function downloadTemplate(id) {
  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/user_management/`,
    data: {
      operation: "donwloadTemplate",
      id: id,
    },
    type: "POST",
    xhrFields: {
      responseType: "blob",
    },
    dataType: "binary",
    success: function (response) {
      var a = window.document.createElement("a");
      var binaryData = [];
      binaryData.push(response);
      a.href = window.URL.createObjectURL(
        new Blob(binaryData, { type: "text/csv" })
      );
      if (id == "downloadUserFileTemplate") {
        a.download = "user_approval.csv";
      } else if (id == "downloadUserGroupTemplate") {
        a.download = "user_group.csv";
      } else if (id == "downloadGroupPermissionsTemplate") {
        a.download = "group_permission.csv";
      } else if (id == "downloadUserWithGroupTemplate") {
        a.download = "usergroup_approval.csv";
      }
      window.document.body.appendChild(a);
      a.click();
      window.document.body.removeChild(a);
    },
    error: function () {},
  });
}

function getPermissionTableData() {
  var groupNameAjax = $("#select_user_group").val();
  if (groupNameAjax && groupNameAjax.length > 0) {
    $(".view_permission_card").css("display", "block");
    $.ajax({
      url: `/users/${app_code2}/${current_dev_mode2}/user_management/`,
      data: {
        operation: "fetch_group_permissions",
        group_name: JSON.stringify(groupNameAjax),
      },
      type: "POST",
      dataType: "json",
      success: function (data) {
        let permissionArray = data.permission_list;
        if ($.fn.dataTable.isDataTable("#example_viewpermissions")) {
          $("#example_viewpermissions").DataTable().clear().destroy();
        }
        for (const perm in permissionArray) {
          delete permissionArray[perm]["app_name"];
          delete permissionArray[perm]["app_code"];
          delete permissionArray[perm]["action"];
        }
        var column_permission_group = [
          { data: "user", mData: "user" },
          { data: "type", mData: "type" },
          { data: "level", mData: "level" },
          { data: "name", mData: "name" },
          { data: "created_by", mData: "created_by" },
        ];
        $("#example_viewpermissions")
          .DataTable({
            data: permissionArray,
            columns: column_permission_group,
            autoWidth: true,
            scrollY: 200,
            scrollX: 500,
            scrollCollapse: true,
            bSort: false,
            orderCellsTop: true,
            responsive: true,
            colReorder: {
              fixedColumnsLeft: 1,
            },
            deferRender: true,
            paging: true,
            lengthMenu: [
              [1, 5, 50, 100, -1],
              [1, 5, 50, 100, "All"],
            ],
            pageLength: 50,
            search: false,
            columnDefs: [
              {
                targets: "_all",
                className: "dt-center allColumnClass all",
              },
            ],
          })
          .columns.adjust();
        $("#example_viewpermissions").on(
          "column-visibility.dt",
          function (e, settings, column, state) {
            $("#example_viewpermissions").DataTable().columns.adjust();
          }
        );
        $(document).on("shown.bs.modal", function (e) {
          $.fn.dataTable.tables({ visible: true, api: true }).columns.adjust();
        });

        $("[name=example_viewpermissions_length]")
          .closest("label")
          .css("display", "flex");
        $("[name=example_viewpermissions_length]")
          .closest("label")
          .css("align-items", "center");
        $("[name=example_viewpermissions_length]")
          .closest("label")
          .css("gap", "9px");
        $("[name=example_viewpermissions_length]")
          .closest(".col-sm-12.col-md-6")
          .css("padding-left", "1rem");
        $("[name=example_viewpermissions_length]").select2({
          width: "50%",
        });

        $("#example_viewpermissions_filter")
          .find("input[type=search]")
          .attr(
            "style",
            "border-radius: 1.8rem !important;border: 1px solid lightgrey !important;height: 28px;padding: 4px 9px;"
          );
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.log("errorr", jqXHR, textStatus, errorThrown);
      },
    });
  }
}

function manageUser(
  id,
  username,
  first_name,
  last_name,
  email,
  role,
  profile_pic,
  first_initial,
  last_initial
) {
  $("#ManageUserModal").attr("data-userid", id);
  $("#ManageUserModal").find(".manage_user_modal").empty();

  $("#ManageUserModal")
    .find("#saveManageUser")
    .attr(
      "onclick",
      `saveManageUser('${id}', '${username}', '${first_name}', '${last_name}', '${email}', '${role}','${user_group_list[username]}')`
    );

  $("#ManageUserGroupsAndPermissions")
    .find("#saveUserGroupDetails")
    .attr(
      "onclick",
      `saveUserGroupDetails('${id}', '${username}', '${first_name}', '${last_name}', '${email}', '${role}','${user_group_list[username]}')`
    );

  $("#reset-password").attr("data-user", username);
  $("#save_reset_password").attr("data-user", username);

  if (first_name) {
    initials = first_initial + last_initial;
  } else {
    initials = username[0];
  }

  if (role == "No Access Assigned") {
    role_html = `<div class="roles-ui-buttons no-role">Unassigned</div>`;
  } else {
    role_html = `<div class="roles-ui-buttons role-user">User</div>`;
    if (role == "Admin") {
      role_html += `<div class="roles-ui-buttons role-admin">Admin</div>`;
    } else if (role == "Developer") {
      role_html += `<div class="roles-ui-buttons role-developer">Developer</div>`;
    } else if (role == "Admin and Developer") {
      role_html += `<div class="roles-ui-buttons role-admin">Admin</div>
          <div class="roles-ui-buttons role-developer">Developer</div>`;
    }
  }

  if (profile_pic) {
    img_html = `<img src="/media/${profile_pic}" class="img-circle elevation-2 mx-auto user-profile-photo" alt="User profile picture" >`;
  } else {
    img_html = `<span  class="profile-initials">${initials}</span>`;
  }

  $("#ManageUserModal")
    .find(".user_details")
    .find(".manage-user-profile")
    .html(img_html);
  $("#ManageUserModal")
    .find(".user_details")
    .find(".col-additional-info")
    .text(username);
  $("#ManageUserModal")
    .find(".user_details")
    .find(".col-username")
    .text(first_name + " " + last_name);

  $("#ManageUserModal").find(".manage_user_modal").append(role_html);
  $("#ManageUserModal").find("#first_name").val(first_name);
  $("#ManageUserModal").find("#last_name").val(last_name);
  $("#ManageUserModal").find("#email").val(email);

  $("#ManageUserModal")
    .find("#assign_user_groups")
    .val(user_group_list[username])
    .trigger("change");
  $("#ManageUserModal").find("#assign_user_groups").prop("disabled", true);

  $("#ManageUserGroupsAndPermissions")
    .find("#select_user_group")
    .off("select2:select");
  $("#ManageUserGroupsAndPermissions")
    .find("#select_user_group")
    .val(user_group_list[username])
    .trigger("change");

  $("#ManageUserGroupsAndPermissions")
    .find("#select_user_group")
    .on("select2:select", function (e) {
      var selectedOption = e.params.data.text;
      new_users_groups_global.push(selectedOption);
    });

  $("#ManageUserGroupsAndPermissions")
    .find("#select_user_group")
    .on("select2:unselect", function (e) {
      var selectedOption = e.params.data.text;
      if (new_users_groups_global.includes(selectedOption)) {
        new_users_groups_global.pop(selectedOption);
      }
    });
}

function saveManageUser(
  id,
  username,
  first_name,
  last_name,
  email,
  role,
  group
) {
  var new_first_name = $(".user_manage_details").find("#first_name").val();
  var new_last_name = $(".user_manage_details").find("#last_name").val();
  var new_email = $(".user_manage_details").find("#email").val();
  var new_group = $(".user_manage_groups").find("#assign_user_groups").val();
  var user_id = id;
  var old_first_name = first_name;
  var old_last_name = last_name;
  var old_email = email;
  var old_group = group.split(",");
  var changedStatus = {};
  let result = true
  var first_name_changed, last_name_changed, email_changed;

  if (new_first_name.trim() != old_first_name.trim()) {
    changedStatus["first_name"] = new_first_name;
    first_name_changed = true;
  }
  if (new_last_name.trim() != old_last_name.trim()) {
    changedStatus["last_name"] = new_last_name;
    last_name_changed = true;
  }
  if (new_email.trim() != old_email.trim()) {
    changedStatus["email"] = new_email;
    email_changed = true;
  }
  if (Object.keys(changedStatus).length > 0){
    for (let i in changedStatus){
      let check_html = /<|>|'|"/.test(changedStatus[i]);
      if(check_html){
        result = false
        break;
      }
    }
  }

  if (!result){
    Swal.fire({
      icon: "error",
      text: "Unauthorised input. Please check and try again.",
    });
  }else{
    if (first_name_changed || last_name_changed || email_changed) {
      $.ajax({
        url: `/users/${app_code2}/${current_dev_mode2}/user_management/`,
        data: {
          user_id: user_id,
          changedStatus: JSON.stringify(changedStatus),
          operation: "save_manage_user",
          username: username,
        },
        dataType: "json",
        type: "POST",
        success: function (response) {
          $("#userTable").DataTable().draw();
          var text = "User Profile details updated successfully!";
          Swal.fire({ icon: "success", text: text });
          $("#ManageUserModal").modal("hide");
        },
        error: function () {
          Swal.fire({
            icon: "error",
            text: "Error! Failure in updating user. Please try again",
          });
          $("#ManageUserModal").modal("hide");
        },
      });
    }
  }
}

function saveUserGroupDetails(
  id,
  username,
  first_name,
  last_name,
  email,
  role,
  group
) {
  var user_id = id;
  var username = username;
  if (new_users_groups_global) {
    $.ajax({
      url: `/users/${app_code2}/${current_dev_mode2}/user_management/`,
      data: {
        user_id: user_id,
        operation: "save_user_group",
        new_users_groups: JSON.stringify(new_users_groups_global),
        username: username,
      },
      dataType: "json",
      type: "POST",
      success: function (response) {
        var text = "Group details are sent for approval.";
        Swal.fire({ icon: "success", text: text });
      },
      error: function () {
        Swal.fire({
          icon: "error",
          text: "Error! Failure in creating user. Please try again",
        });
      },
    });
  }
}

function viewDetailsUserApproval(username, action, email) {
  if ($.fn.dataTable.isDataTable("#viewDetailsUserTable")) {
    $("#viewDetailsUserTable").DataTable().clear().destroy();
  }

  var table_html = `
      <tr>
          <td>${username}</td>
          <td>${email}</td>
          <td>${action}</td>
      </tr>
  `;

  $("#viewDetailsUserModal")
    .find("#viewDetailsUserTable")
    .find("#viewDetailsUserTableBody")
    .html(table_html);
  var table = $("#viewDetailsUserModal")
    .find("#viewDetailsUserTable")
    .DataTable({
      paging: false,
      info: false,
      searching: false,
      bSort: false,
      responsive: true,
    })
    .columns.adjust();
  $("#viewDetailsUserTable").on(
    "column-visibility.dt",
    function (e, settings, column, state) {
      $(`#` + "viewDetailsUserTable")
        .DataTable()
        .columns.adjust();
    }
  );
  $(document).on("shown.bs.modal", function (e) {
    $.fn.dataTable.tables({ visible: true, api: true }).columns.adjust();
  });

  $("#viewDetailsUserModal").modal("show");
}

function viewDetailsPermissionApproval(groupname, level, app_code) {
  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/user_management/`,
    data: {
      groupname: groupname,
      level_of_permission: level,
      operation: "permissionapproval_viewdetails",
      app_code: app_code,
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      if ($.fn.dataTable.isDataTable("#viewDetailsPermissionTable")) {
        $("#viewDetailsPermissionTable").DataTable().clear().destroy();
      }

      var table_html = "";

      for (user_obj of data.data) {
        table_html += `
                  <tr>
                      <td>${user_obj["Group Name"]}</td>
                      <td>${user_obj["Permission Name"]}</td>
                      <td>${user_obj["Application Name"]}</td>
                  </tr>
              `;
      }

      $("#viewDetailsPermissionModal")
        .find("#viewDetailsPermissionTable")
        .find("#viewDetailsPermissionTableBody")
        .html(table_html);
      var table = $("#viewDetailsPermissionModal")
        .find("#viewDetailsPermissionTable")
        .DataTable({
          paging: false,
          info: false,
          searching: false,
          bSort: false,
          responsive: true,
        })
        .columns.adjust();
      $("#viewDetailsPermissionTable").on(
        "column-visibility.dt",
        function (e, settings, column, state) {
          $(`#` + "viewDetailsPermissionTable")
            .DataTable()
            .columns.adjust();
        }
      );
      $(document).on("shown.bs.modal", function (e) {
        $.fn.dataTable.tables({ visible: true, api: true }).columns.adjust();
      });

      $("#viewDetailsPermissionModal").modal("show");
    },
    error: function () {
      Swal.fire({
        icon: "error",
        text: "Error! Failure in exporting data. Please try again.",
      });
    },
  });
}

function viewDetailsUserGroupApproval(username, count_of_approval) {
  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/user_management/`,
    data: {
      user_name: username,
      operation: "view_usergroup_approval_details",
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      if ($.fn.dataTable.isDataTable("#viewDetailsGroupTable")) {
        $("#viewDetailsGroupTable").DataTable().clear().destroy();
      }

      var table_html = "";

      for (user_obj of data.data) {
        table_html += `
                  <tr>
                      <td>${user_obj["User Name"]}</td>
                      <td>${user_obj["Group Name"]}</td>
                  </tr>
              `;
      }

      $("#viewDetailsGroupModal")
        .find("#viewDetailsGroupTable")
        .find("#viewDetailsGroupTableBody")
        .html(table_html);
      var table = $("#viewDetailsGroupModal")
        .find("#viewDetailsGroupTable")
        .DataTable({
          paging: false,
          info: false,
          searching: false,
          bSort: false,
          responsive: true,
        })
        .columns.adjust();
      $("#viewDetailsGroupTable").on(
        "column-visibility.dt",
        function (e, settings, column, state) {
          $(`#` + "viewDetailsGroupTable")
            .DataTable()
            .columns.adjust();
        }
      );
      $(document).on("shown.bs.modal", function (e) {
        $.fn.dataTable.tables({ visible: true, api: true }).columns.adjust();
      });

      $("#viewDetailsGroupModal").modal("show");
    },
    error: function () {
      Swal.fire({
        icon: "error",
        text: "Error! Failure in exporting data. Please try again.",
      });
    },
  });
}

function groupApproval() {
  $("#modal-table-header").empty();
  $("#modal-table-body").empty();
  $("#approvaldownmodal").modal("show");
  var username = $(this).closest("tr").attr("data-username");

  let url_string = window.location.pathname;
  let f_occ = url_string.indexOf("/", url_string.indexOf("/") + 1);
  let s_occ = url_string.indexOf("/", url_string.indexOf("/") + f_occ + 1);
  let t_occ = url_string.indexOf("/", url_string.indexOf("/") + s_occ + 1);
  let app_code2 = url_string.substring(f_occ + 1, s_occ);
  let current_dev_mode2 = url_string.substring(s_occ + 1, t_occ);
  let modes = ["Build", "Edit"];
  let url = "";
  if (current_dev_mode2 != "Build" && current_dev_mode2 != "Edit") {
    current_dev_mode2 = "User";
  }
  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/permissionapproval/`,
    data: {
      user_name: username,
      operation: "approval_table",
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      $("#approvalmodal_heading").text(username);

      for (const column_name of data.columns) {
        $("#modal-table-header").append(`<th>${column_name}</th>`);
      }
      $("#modal-table-header").append("<th>Approve</th>");
      var counter = 0;
      for (const ind_dict of data.data) {
        html = "";
        for (const column_name of data.columns) {
          html += `<th>${ind_dict[column_name]}</th>`;
        }
        html += `<td><button id="approve_${data.approve_id[counter]}" type="button" class="approve_ind btn btn-floating btn-lg" style="color:var(--primary-color) !important;"><i class="fa fa-check-square" aria-hidden="true"></i></button><button id="reject_${data.approve_id[counter]}" type="button" class="reject_ind btn btn-floating btn-lg" style="color:#000000;"><i class="fa fa-window-close" aria-hidden="true"></i></button></td>`;
        $("#modal-table-body").append("<tr>" + html + "</tr>");
        counter++;
      }
      $(".approve_ind").on("click", approve_ind);
      $(".reject_ind").on("click", reject_ind);
      if (!$.fn.dataTable.isDataTable("#approval_table")) {
        var tablemodal1 = $("#approval_table").DataTable({
          autoWidth: true,
          paging: false,
          info: false,
          searching: false,
          bSort: false,
          responsive: true,
          paging: true,
          lengthMenu: [
            [1, 5, 50, 100, -1],
            [1, 5, 50, 100, "All"],
          ],
          stripeClasses: false,
          pageLength: 50,

          columnDefs: [
            {
              targets: "_all",
              className: "dt-center allColumnClass all",
            },
            {
              targets: 0,
              width: "20%",
              className: "noVis",
            },
          ],
        });
      }
    },
    error: function () {
      Swal.fire({
        icon: "error",
        text: "Error! Failure in exporting data. Please try again.",
      });
    },
  });
}

function approve_ind() {
  let refer = $(this);
  $(this).prop("disabled", true);
  $(this).attr("disabled", "disabled");
  var groupname = $(this).closest("tr").attr("data-groupname");
  let user_name = $(this).closest("tr").attr("data-username");

  let approval_table_id = Number($(this).attr("id").split("_")[1]);
  let reject_row_id = "reject_" + approval_table_id;

  $("#" + reject_row_id).prop("disabled", true);
  $("#" + reject_row_id).attr("disabled", "disabled");
  let url_string = window.location.pathname;
  let f_occ = url_string.indexOf("/", url_string.indexOf("/") + 1);
  let s_occ = url_string.indexOf("/", url_string.indexOf("/") + f_occ + 1);
  let t_occ = url_string.indexOf("/", url_string.indexOf("/") + s_occ + 1);
  let app_code2 = url_string.substring(f_occ + 1, s_occ);
  let current_dev_mode2 = url_string.substring(s_occ + 1, t_occ);
  let modes = ["Build", "Edit"];
  let url = "";
  if (current_dev_mode2 != "Build" && current_dev_mode2 != "Edit") {
    current_dev_mode2 = "User";
  }
  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/permissionapproval/`,
    data: {
      userName: user_name,
      groupName: groupname,
      approval_id: approval_table_id,
      operation: "approve_ind",
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      Swal.fire({
        icon: "info",
        text:
          "Approved group " +
          groupname +
          " for user " +
          user_name +
          ". Permissions for users are getting updated. Please check the Notifications bell for further updates.",
      });

      remove_tr = refer.closest("tr");
      let approvaltable = $("#user_access_approvals_table").DataTable();
      approvaltable.row(remove_tr).remove().draw();
    },
    error: function () {
      Swal.fire({
        icon: "error",
        text: "Error! Failure in updating permissions. Please try again.",
      });
    },
  });
}
function reject_ind() {
  let refer = $(this);
  $(this).prop("disabled", true);
  $(this).attr("disabled", "disabled");
  var groupname = $(this).closest("tr").attr("data-groupname");

  let user_name = $(this).closest("tr").attr("data-username");

  let approval_table_id = Number($(this).attr("id").split("_")[1]);

  let approve_row_id = "approve_" + approval_table_id;

  $("#" + approve_row_id).prop("disabled", true);
  $("#" + approve_row_id).attr("disabled", "disabled");

  let url_string = window.location.pathname;
  let f_occ = url_string.indexOf("/", url_string.indexOf("/") + 1);
  let s_occ = url_string.indexOf("/", url_string.indexOf("/") + f_occ + 1);
  let t_occ = url_string.indexOf("/", url_string.indexOf("/") + s_occ + 1);
  let app_code2 = url_string.substring(f_occ + 1, s_occ);
  let current_dev_mode2 = url_string.substring(s_occ + 1, t_occ);
  let modes = ["Build", "Edit"];
  let url = "";
  if (current_dev_mode2 != "Build" && current_dev_mode2 != "Edit") {
    current_dev_mode2 = "User";
  }

  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/permissionapproval/`,
    data: {
      userName: user_name,
      approval_id: approval_table_id,
      operation: "reject_ind",
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      Swal.fire({
        icon: "success",
        text:
          "Rejected group " +
          groupname +
          " for user " +
          user_name +
          " successfully!",
      });

      remove_tr = refer.closest("tr");
      let approvaltable = $("#user_access_approvals_table").DataTable();
      approvaltable.row(remove_tr).remove().draw();
    },
    error: function () {
      Swal.fire({
        icon: "error",
        text: "Error! Failure in executing rejection. Please try again.",
      });
    },
  });
}

function approve_all() {
  let user_name = $("#approvalmodal_heading").text().replace(": ", "");
  let url_string = window.location.pathname;
  let f_occ = url_string.indexOf("/", url_string.indexOf("/") + 1);
  let s_occ = url_string.indexOf("/", url_string.indexOf("/") + f_occ + 1);
  let t_occ = url_string.indexOf("/", url_string.indexOf("/") + s_occ + 1);
  let app_code2 = url_string.substring(f_occ + 1, s_occ);
  let current_dev_mode2 = url_string.substring(s_occ + 1, t_occ);
  let modes = ["Build", "Edit"];
  let url = "";
  if (current_dev_mode2 != "Build" && current_dev_mode2 != "Edit") {
    current_dev_mode2 = "User";
  }
  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/permissionapproval/`,
    data: {
      userName: user_name,
      operation: "approve_all",
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      Swal.fire({
        icon: "info",
        text: "Approved successfully! Permissions for users are getting updated. Please check the Notifications bell for further updates.",
      });
      $(`#userTable`).DataTable().draw();
    },
    error: function () {
      Swal.fire({
        icon: "error",
        text: "Error! Failure in executing approvals. Please try again.",
      });
    },
  });
}
function reject_all() {
  let user_name = $("#approvalmodal_heading").text().replace(": ", "");
  let url_string = window.location.pathname;
  let f_occ = url_string.indexOf("/", url_string.indexOf("/") + 1);
  let s_occ = url_string.indexOf("/", url_string.indexOf("/") + f_occ + 1);
  let t_occ = url_string.indexOf("/", url_string.indexOf("/") + s_occ + 1);
  let app_code2 = url_string.substring(f_occ + 1, s_occ);
  let current_dev_mode2 = url_string.substring(s_occ + 1, t_occ);
  let modes = ["Build", "Edit"];
  let url = "";
  if (current_dev_mode2 != "Build" && current_dev_mode2 != "Edit") {
    current_dev_mode2 = "User";
  }
  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/permissionapproval/`,
    data: {
      userName: user_name,
      operation: "reject_all",
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      Swal.fire({ icon: "success", text: "Rejected approvals successfully!" });
    },
    error: function () {
      Swal.fire({
        icon: "error",
        text: "Error! Failure in executing rejection of approvals. Please try again.",
      });
    },
  });
}

function userApproval() {
  var refer = $(this);
  var username = $(this).closest("tr").attr("data-username");
  var password = $(this).closest("tr").attr("data-password");
  var email = $(this).closest("tr").attr("data-email");
  var type = $(this).closest("tr").attr("data-type");
  var is_developer = $(this).closest("tr").attr("data-developer");
  var action = $(this).closest("tr").attr("data-action");
  let url_string = window.location.pathname;
  let f_occ = url_string.indexOf("/", url_string.indexOf("/") + 1);
  let s_occ = url_string.indexOf("/", url_string.indexOf("/") + f_occ + 1);
  let t_occ = url_string.indexOf("/", url_string.indexOf("/") + s_occ + 1);
  let app_code2 = url_string.substring(f_occ + 1, s_occ);
  let current_dev_mode2 = url_string.substring(s_occ + 1, t_occ);
  if (current_dev_mode2 != "Build" && current_dev_mode2 != "Edit") {
    current_dev_mode2 = "User";
  }
  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/permissionapproval/`,

    data: {
      operation: "userapproval",
      username: username,
      password: password,
      email: email,
      action: action,
      type: type,
      is_developer: is_developer,
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      if (data.icon == "warning") {
        Swal.fire({ icon: "warning", text: data.response });
      } else {
        Swal.fire({ icon: "success", text: "Approved successfully" });

        remove_tr = refer.closest("tr");
        let approvaltable = $("#user_access_approvals_table").DataTable();
        approvaltable.row(remove_tr).remove().draw();

        pending_approvals = parseInt($(".approval_notification_badge").text());

        if (pending_approvals - 1 < 1) {
          $(".approval_notification_badge").text("0");
          $(".approval_notification_badge").css("display", "none");
        } else {
          $(".approval_notification_badge").text(pending_approvals - 1);
        }
        if (data.data == "error") {
          Swal.fire({ icon: "error", text: data.msg });
        }
      }
    },
    error: function () {
      Swal.fire({ icon: "error", text: "Error! Please try again." });
    },
  });
}

function userReject() {
  var refer = $(this);
  var username = $(this)
    .closest("tr")
    .find("td:first-child")
    .attr("data-username");
  var password = $(this)
    .closest("tr")
    .find("td:first-child")
    .attr("data-password");
  var email = $(this).closest("tr").find("td:first-child").attr("data-email");
  let url_string = window.location.pathname;
  let f_occ = url_string.indexOf("/", url_string.indexOf("/") + 1);
  let s_occ = url_string.indexOf("/", url_string.indexOf("/") + f_occ + 1);
  let t_occ = url_string.indexOf("/", url_string.indexOf("/") + s_occ + 1);
  let app_code2 = url_string.substring(f_occ + 1, s_occ);
  let current_dev_mode2 = url_string.substring(s_occ + 1, t_occ);
  let modes = ["Build", "Edit"];
  let url = "";
  if (current_dev_mode2 != "Build" && current_dev_mode2 != "Edit") {
    current_dev_mode2 = "User";
  }
  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/permissionapproval/`,
    data: {
      operation: "userrejection",
      username: username,
      password: password,
      email: email,
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      Swal.fire({ icon: "success", text: "Rejected successfully" });

      remove_tr = refer.closest("tr");
      let approvaltable = $("#user_access_approvals_table").DataTable();
      approvaltable.row(remove_tr).remove().draw();

      pending_approvals = parseInt($(".approval_notification_badge").text());

      if (pending_approvals - 1 < 1) {
        $(".approval_notification_badge").text("0");
        $(".approval_notification_badge").css("display", "none");
      } else {
        $(".approval_notification_badge").text(pending_approvals - 1);
      }
    },
    error: function () {
      Swal.fire({ icon: "error", text: "Error! Please try again." });
    },
  });
}

function approvePermissions() {
  $("#modal-table-header-permission").empty();
  $("#modal-table-body-permission").empty();
  $("#permissiondownmodal").modal("show");
  var groupname = $(this).closest("tr").attr("data-groupname");
  var level = $(this).closest("tr").attr("data-level");

  let url_string = window.location.pathname;
  let f_occ = url_string.indexOf("/", url_string.indexOf("/") + 1);
  let s_occ = url_string.indexOf("/", url_string.indexOf("/") + f_occ + 1);
  let t_occ = url_string.indexOf("/", url_string.indexOf("/") + s_occ + 1);
  let app_code2 = url_string.substring(f_occ + 1, s_occ);
  let current_dev_mode2 = url_string.substring(s_occ + 1, t_occ);
  let modes = ["Build", "Edit"];
  let url = "";
  if (current_dev_mode2 != "Build" && current_dev_mode2 != "Edit") {
    current_dev_mode2 = "User";
  }
  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/permissionapproval/`,
    data: {
      groupname: groupname,
      level_of_permission: level,
      operation: "permissionapproval_table",
      app_code: $(this).attr("data-app_code"),
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      $("#permissionmodal_heading").text(`(User Group : ${groupname})`);
      $("#permissionmodal_level").text(level);

      for (const column_name of data.columns) {
        $("#modal-table-header-permission").append(`<th>${column_name}</th>`);
      }
      $("#modal-table-header-permission").append("<th>Approve</th>");
      var counter = 0;
      for (const ind_dict of data.data) {
        html = "";
        for (const column_name of data.columns) {
          html += `<td>${ind_dict[column_name]}</td>`;
        }
        html += `<td><button id="approve_${data.count_id[counter]}" data-app_code="${ind_dict["app_code"]}" type="button" class="approve_ind_permission btn btn-primary btn-xs rounded mb-1 px-2" style="color:var(--primary-color) !important;background-color:unset !important;border:0;margin-bottom: 0 !important;"><i class="fas fa-check-circle" style="font-size: large;"></i></button><button id="reject_${data.count_id[counter]}" data-app_code="${ind_dict["app_code"]}" type="button" class="reject_ind_permission btn btn-primary btn-xs rounded mb-1 px-2" style="color:var(--primary-color) !important;background-color:unset !important;border:0;margin-bottom: 0 !important;"><i class="fa-solid fa-circle-xmark" style="font-size: large;"></i></button></td>`;
        $("#modal-table-body-permission").append("<tr>" + html + "</tr>");
        counter++;
      }
      if (
        $(".approve_ind_permission").eq(0).attr("id") ==
        "approve_Administrative access"
      ) {
        $("#approve_all_permission").prop("disabled", true);
        $("#reject_all_permission").prop("disabled", true);
      } else {
        $("#approve_all_permission").prop("disabled", false);
        $("#reject_all_permission").prop("disabled", false);
      }
      $(".approve_ind_permission").on("click", approve_ind_permission);
      $(".reject_ind_permission").on("click", reject_ind_permission);
      if (!$.fn.dataTable.isDataTable("#permission_table")) {
        var tablemodal1 = $("#permission_table").DataTable({
          autoWidth: true,
          scrollCollapse: true,
          orderCellsTop: true,
          responsive: true,
          bSort: false,
          colReorder: {
            fixedColumnsLeft: 1,
          },
          stateSave: true,
          deferRender: true,
          paging: true,
          lengthMenu: [
            [1, 5, 50, 100, -1],
            [1, 5, 50, 100, "All"],
          ],
          stripeClasses: false,
          pageLength: 50,
          columnDefs: [
            {
              targets: "_all",
              className: "dt-center allColumnClass all",
            },
            {
              targets: 0,
              width: "20%",
              className: "noVis",
            },
          ],
        });

        $("#permission_table_length")
          .parent()
          .attr("class", "col-sm-12 col-md-3");
        $("#permission_table_filter")
          .parent()
          .attr("class", "col-sm-12 col-md-5 d-flex justify-content-start");
        $("#permission_table_filter").find("label").css("font-size", "0.8rem");
        $("#permission_table_filter")
          .parent()
          .after($(".permission-approve-reject"));
      }
    },
    error: function () {
      Swal.fire({
        icon: "error",
        text: "Error! Failure in exporting data. Please try again.",
      });
    },
  });
}

function approve_ind_permission() {
  $(this).prop("disabled", true);
  $(this).attr("disabled", "disabled");
  let groupname = $("#permissionmodal_heading")
    .text()
    .split(":")[1]
    .split(")")[0]
    .trim();
  let permission_level = $("#permissionmodal_level").text();

  let approval_table_id = Number($(this).attr("id").split("_")[1]);
  let reject_row_id = "reject_" + approval_table_id;
  $("#" + reject_row_id).prop("disabled", true);
  $("#" + reject_row_id).attr("disabled", "disabled");
  let url_string = window.location.pathname;
  let f_occ = url_string.indexOf("/", url_string.indexOf("/") + 1);
  let s_occ = url_string.indexOf("/", url_string.indexOf("/") + f_occ + 1);
  let t_occ = url_string.indexOf("/", url_string.indexOf("/") + s_occ + 1);
  let app_code2 = url_string.substring(f_occ + 1, s_occ);
  let current_dev_mode2 = url_string.substring(s_occ + 1, t_occ);
  let modes = ["Build", "Edit"];
  let url = "";
  if (current_dev_mode2 != "Build" && current_dev_mode2 != "Edit") {
    current_dev_mode2 = "User";
  }
  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/userpermissionapproval/`,
    data: {
      groupName: groupname,
      level: permission_level,
      approval_id: approval_table_id,
      operation: "approve_ind_permission",
      app_code: $(this).attr("data-app_code"),
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      Swal.fire({
        icon: "success",
        text: "Approved successfully! Permissions for users are getting updated. Please check the Notifications bell for further updates.",
      });
      $(`#userTable`).DataTable().draw();
    },
    error: function () {
      Swal.fire({
        icon: "error",
        text: "Error! Failure in approving permission. Please try again.",
      });
    },
  });
}
function reject_ind_permission() {
  $(this).prop("disabled", true);
  $(this).attr("disabled", "disabled");
  let groupname = $("#permissionmodal_heading")
    .text()
    .split(":")[1]
    .split(")")[0]
    .trim();

  let approval_table_id = Number($(this).attr("id").split("_")[1]);
  let approve_row_id = "approve_" + approval_table_id;
  let level = $("#permissionmodal_level").text();

  $("#" + approve_row_id).prop("disabled", true);
  $("#" + approve_row_id).attr("disabled", "disabled");
  let url_string = window.location.pathname;
  let f_occ = url_string.indexOf("/", url_string.indexOf("/") + 1);
  let s_occ = url_string.indexOf("/", url_string.indexOf("/") + f_occ + 1);
  let t_occ = url_string.indexOf("/", url_string.indexOf("/") + s_occ + 1);
  let app_code2 = url_string.substring(f_occ + 1, s_occ);
  let current_dev_mode2 = url_string.substring(s_occ + 1, t_occ);
  let modes = ["Build", "Edit"];
  let url = "";
  if (current_dev_mode2 != "Build" && current_dev_mode2 != "Edit") {
    current_dev_mode2 = "User";
  }
  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/userpermissionrejection/`,
    data: {
      groupName: groupname,
      level: level,
      approval_id: approval_table_id,
      operation: "reject_ind_permission",
      app_code: $(this).attr("data-app_code"),
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      Swal.fire({
        icon: "success",
        text: "Permission successfully rejected!.",
      });
    },
    error: function () {
      Swal.fire({
        icon: "error",
        text: "Error! Failure in rejecting permission. Please try again.",
      });
    },
  });
}

function userAccessHandler() {
  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/user_management/`,
    data: {
      operation: "fetch_pending_user_access_approvals",
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      let approvalTableElement = $("#user_access_approvals_table > tbody");
      let requestsTableElement = $("#user_requests_table > tbody");

      approvalTableElement.empty();
      requestsTableElement.empty();

      let userApprovalTableHTML = "";
      let userRequestsTableHTML = "";

      if (data.combined_approvals_sorted) {
        for (const iterator of data.combined_approvals_sorted) {
          if (iterator.approval_type == "user_approval") {
            if (iterator.can_approve == "Yes") {
              let userApprovalHTML = "";
              let uARow = `<tr data-username="${iterator.username}" data-action="${iterator.action_requested}" data-email="${iterator.email}" data-password="${iterator.password}" data-type="${iterator.authentication_type}" data-developer="${iterator.is_developer}">`;
              if (iterator.can_approve == "Yes") {
                uARow += `
                              <td data-username="${iterator.username}" data-action="${iterator.action_requested}" data-email="${iterator.email}" data-password="${iterator.password}" data-type="${iterator.authentication_type}" data-developer="${iterator.is_developer}">
                                  <button type="button"  data-toggle="tooltip" title="Approve User Permission" class="userpermission_approve btn btn-primary btn-xs rounded mb-1 px-2" style="color:var(--primary-color) !important;background-color:unset !important;border:0"><i class="fas fa-check-circle" style="font-size: large;"></i></button>
                                  <button type="button" data-toggle="tooltip" title="Reject User Permission" class="userpermission_reject btn btn-primary btn-xs rounded mb-1 px-2" style="color:var(--primary-color) !important;background-color:unset !important;border:0"><i class="fa-solid fa-circle-xmark" style="font-size: large;"></i></button>
                              </td>
                              `;
              } else {
                uARow += `
                              <td data-username="${iterator.username}" data-action="${iterator.action_requested}" data-email="${iterator.email}" data-password="${iterator.password}" data-type="${iterator.authentication_type}" data-developer="${iterator.is_developer}">
                                  <button type="button"  data-toggle="tooltip" title="Pending for approval" disabled  class="userpermission_approve btn btn-primary btn-xs rounded mb-1 px-2" style="color:var(--primary-color) !important;background-color:unset !important;border:0"><i class="fas fa-check-circle" style="font-size: large;"></i></button>
                                  <button type="button" data-toggle="tooltip" title="Pending for rejection" disabled class="userpermission_reject btn btn-primary btn-xs rounded mb-1 px-2" style="color:var(--primary-color) !important;background-color:unset !important;border:0"><i class="fa-solid fa-circle-xmark" style="font-size: large;"></i></button>
                              </td>
                              `;
              }
              uARow += `<td><button class="btn btn-light" class="view_details_user_approval" onclick="viewDetailsUserApproval('${iterator.username}','${iterator.action_requested}','${iterator.email}')">View Details</button></td>`;
              if (iterator.action_requested == "new user") {
                uARow += "<td>New user request</td>";
              } else {
                uARow += "<td>Delete user request</td>";
              }
              uARow += `<td>${iterator.username}</td>`;
              uARow += `<td>${iterator.created_by}</td>`;
              uARow += `<td>${iterator.created_date}</td>`;
              uARow += "</tr>";
              userApprovalHTML += uARow;
              userApprovalTableHTML += userApprovalHTML;
            } else {
              let userApprovalHTML = "";
              let uARow = `<tr data-username="${iterator.username}" data-action="${iterator.action_requested}" data-email="${iterator.email}" data-password="${iterator.password}" data-type="${iterator.authentication_type}" data-developer="${iterator.is_developer}">`;

              uARow += `<td><button class="btn btn-light" class="view_details_user_approval" onclick="viewDetailsUserApproval('${iterator.username}','${iterator.action_requested}','${iterator.email}')">View Details</button></td>`;
              if (iterator.action_requested == "new user") {
                uARow += "<td>New user request</td>";
              } else {
                uARow += "<td>Delete user request</td>";
              }
              uARow += `<td>${iterator.username}</td>`;
              uARow += `<td>${iterator.created_by}</td>`;
              uARow += `<td>${iterator.created_date}</td>`;
              uARow += "</tr>";
              userApprovalHTML += uARow;
              userRequestsTableHTML += userApprovalHTML;
            }
          }
          if (iterator.approval_type == "group_approval") {
            if (iterator.can_approve == "Yes") {
              let userGroupApprovalHTML = "";
              let uGARow = `<tr data-username="${iterator.user_name}" data-groupname="${iterator.group_name}">`;
              if (iterator.can_approve == "Yes") {
                uGARow += `
                              <td>
                                  <button id="approve_${iterator.id}" type="button" data-toggle="tooltip" title="Pending for approval" class="approve_ind btn btn-primary btn-xs rounded mb-1 px-2" style="color:var(--primary-color) !important;background-color:unset !important;border:0"><i class="fa fa-check-circle" style="font-size: large;" aria-hidden="true"></i></button>
                                  <button id="reject_${iterator.id}" type="button" data-toggle="tooltip" title="Pending for rejection" class="reject_ind btn btn-primary btn-xs rounded mb-1 px-2" style="color:var(--primary-color) !important;background-color:unset !important;border:0"><i class="fa fa-circle-xmark" style="font-size: large;" aria-hidden="true"></i></button>
                              </td>`;
              } else {
                uGARow += `
                              <td>
                                  <button id="approve_${iterator.id}" type="button" disabled class="approve_ind btn btn-primary btn-xs rounded mb-1 px-2" style="color:var(--primary-color) !important;background-color:unset !important;border:0"><i class="fa fa-check-circle" style="font-size: large;" aria-hidden="true"></i></button>
                                  <button id="reject_${iterator.id}" type="button" disabled class="reject_ind btn btn-primary btn-xs rounded mb-1 px-2" style="color:var(--primary-color) !important;background-color:unset !important;border:0"><i class="fa fa-circle-xmark" style="font-size: large;" aria-hidden="true"></i></button>
                              </td>`;
              }
              uGARow += `<td><button class="btn btn-light" onclick="viewDetailsUserGroupApproval('${iterator.user_name}','${iterator.count_of_approval}')">View Details</button></td>`;
              uGARow += "<td>New user group request</td>";
              uGARow += `<td>${iterator.user_name}</td>`;
              uGARow += `<td>${iterator.created_by}</td>`;
              uGARow += `<td>${iterator.created_date}</td>`;
              uGARow += "</tr>";
              userGroupApprovalHTML += uGARow;
              userApprovalTableHTML += userGroupApprovalHTML;
            } else {
              let userGroupApprovalHTML = "";
              let uGARow = `<tr data-username="${iterator.user_name}" data-groupname="${iterator.group_name}">`;

              uGARow += `<td><button class="btn btn-light" onclick="viewDetailsUserGroupApproval('${iterator.user_name}','${iterator.count_of_approval}')">View Details</button></td>`;
              uGARow += "<td>New user group request</td>";
              uGARow += `<td>${iterator.user_name}</td>`;
              uGARow += `<td>${iterator.created_by}</td>`;
              uGARow += `<td>${iterator.created_date}</td>`;
              uGARow += "</tr>";
              userGroupApprovalHTML += uGARow;
              userRequestsTableHTML += userGroupApprovalHTML;
            }
          }
          if (iterator.approval_type == "permission_approval") {
            if (iterator.can_approve == "Yes") {
              let permissionApprovalHTML = "";
              let permRow = `<tr data-groupname="${iterator.usergroup}" data-level="${iterator.permission_level}">`;
              if (iterator.can_approve == "Yes") {
                permRow += `
                              <td>
                                  <button type="button" data-app_code="${iterator.app_code}" data-toggle="tooltip" title="Approve Group Permission" class="permission_button btn btn-light btn-md">Click Here</button>
                              </td>
                              `;
              } else {
                permRow += `<td><button type="button" disabled data-app_code="${iterator.app_code}" data-toggle="tooltip" title="Approve Group Permission" class="permission_button btn btn-light btn-md " >Click Here</button></td>`;
              }
              permRow += `<td><button class="btn btn-light" onclick="viewDetailsPermissionApproval('${iterator.usergroup}','${iterator.permission_level}','${iterator.app_code}')">View Details</button></td>`;
              permRow += "<td>New group permission request</td>";
              permRow += `<td>${iterator.usergroup}</td>`;
              permRow += `<td>${iterator.created_by}</td>`;
              permRow += `<td>${iterator.created_date}</td>`;
              permRow += "</tr>";
              permissionApprovalHTML += permRow;
              userApprovalTableHTML += permissionApprovalHTML;
            } else {
              let permissionApprovalHTML = "";
              let permRow = `<tr data-groupname="${iterator.usergroup}" data-level="${iterator.permission_level}">`;

              permRow += `<td><button class="btn btn-light" onclick="viewDetailsPermissionApproval('${iterator.usergroup}','${iterator.permission_level}','${iterator.app_code}')">View Details</button></td>`;
              permRow += "<td>New group permission request</td>";
              permRow += `<td>${iterator.usergroup}</td>`;
              permRow += `<td>${iterator.created_by}</td>`;
              permRow += `<td>${iterator.created_date}</td>`;
              permRow += "</tr>";
              permissionApprovalHTML += permRow;
              userRequestsTableHTML += permissionApprovalHTML;
            }
          }
        }
        approvalTableElement.append(userApprovalTableHTML);
        requestsTableElement.append(userRequestsTableHTML);
      }

      var approval_table, requests_table;

      if ($.fn.dataTable.isDataTable("#user_access_approvals_table")) {
        $("#user_access_approvals_table").DataTable().destroy();
      }

      if ($.fn.dataTable.isDataTable("#user_requests_table")) {
        $("#user_requests_table").DataTable().destroy();
      }

      $.fn.dataTable.ext.order["date-format"] = function (settings, col) {
        return this.api()
          .column(col, { order: "index" })
          .nodes()
          .map(function (td, i) {
            var dateString = $(td)
              .text()
              .replace(
                /(\d+)[^\d]+(\d+)[^\d]+(\d+)[^\d]+(\d+):(\d+)\s*([APMapm]+)\s*\./,
                "$1-$2-$3 $4:$5 $6"
              );
            return new Date(dateString);
          });
      };

      approval_table = $("#user_access_approvals_table")
        .DataTable({
          autoWidth: true,
          scrollY: 250,
          scrollX: 500,
          scrollCollapse: true,
          searching: true,
          search: true,
          bSort: false,
          responsive: true,
          colReorder: {
            fixedColumnsLeft: 1,
          },
          bFilter: true,
          deferRender: true,
          paging: true,
          lengthMenu: [
            [1, 5, 50, 100, -1],
            [1, 5, 50, 100, "All"],
          ],
          pageLength: 50,
          columnDefs: [
            {
              targets: "_all",
              className: "dt-center allColumnClass all",
            },
            { type: "date-format", targets: 5 },
          ],
          order: [[5, "desc"]],
        })
        .columns.adjust();

      filter_html = `
              <div class="col-sm-12 col-md-12 p-0">
                  <div id="user_access_approvals_table_filter_approval_type" class="datatable_filter_approval_type">
                      <div style="display:flex;align-items:center;">
                          <h6 class="mb-0 mr-2">Approval Type:</h6>
                          <select id="approval_type_filter" style="border-radius:1.8rem">
                              <option value="">All</option>
                              <option value="New user group request">New user group request</option>
                              <option value="New group permission request">New group permission request</option>
                              <option value="New user request">New user request</option>
                              <option value="Delete user request">Delete user request</option>
                          </select>
                      </div>
                  </div>
              </div>`;

      $("#user_access_approvals_table_wrapper")
        .find(".row")
        .eq(0)
        .addClass("mobile-column-reverse");
      $("#user_access_approvals_table_wrapper")
        .find(".row")
        .eq(0)
        .append(filter_html);

      $("#approval_type_filter").select2({
        width: "25%",
      });
      $("[name=user_access_approvals_table_length]")
        .closest("label")
        .css("display", "flex");
      $("[name=user_access_approvals_table_length]")
        .closest("label")
        .css("align-items", "center");
      $("[name=user_access_approvals_table_length]")
        .closest("label")
        .css("gap", "9px");
      $("[name=user_access_approvals_table_length]")
        .closest("label")
        .css("text-indent", "0");
      $("[name=user_access_approvals_table_length]")
        .closest("label")
        .css("padding-left", "7.5px");
      $("[name=user_access_approvals_table_length]").select2({
        width: "50%",
      });

      $("#user_access_approvals_table_filter")
        .find("input[type=search]")
        .attr(
          "style",
          "border-radius: 1.8rem !important;border: 1px solid lightgrey !important;height: 28px;padding: 4px 9px;"
        );
      $("#user_access_approvals_table_filter")
        .parent()
        .attr("class", "col-sm-12 col-md-12 col-lg-6");

      $("#approval_type_filter").on("change", function () {
        var selectedValue = $(this).val();
        if (selectedValue == "") {
          approval_table.column(2).search("");
          approval_table.column(2).draw();
        } else {
          approval_table.column(2).search("");
          approval_table.column(2).draw();
          approval_table
            .column(2)
            .search("^" + selectedValue + "$", true, false);
          approval_table.column(2).draw();
        }
      });

      $("#user_access_approvals_table").on(
        "column-visibility.dt",
        function (e, settings, column, state) {
          $(`#` + "user_access_approvals_table")
            .DataTable()
            .columns.adjust();
        }
      );
      $(document).on("shown.bs.modal", function (e) {
        $.fn.dataTable.tables({ visible: true, api: true }).columns.adjust();
      });

      //

      requests_table = $("#user_requests_table")
        .DataTable({
          autoWidth: true,
          scrollY: 250,
          scrollX: 500,
          scrollCollapse: true,
          searching: true,
          search: true,
          bSort: false,
          responsive: true,
          colReorder: {
            fixedColumnsLeft: 1,
          },
          bFilter: true,
          deferRender: true,
          paging: true,
          lengthMenu: [
            [1, 5, 50, 100, -1],
            [1, 5, 50, 100, "All"],
          ],
          pageLength: 50,
          columnDefs: [
            {
              targets: "_all",
              className: "dt-center allColumnClass all",
            },
            { type: "date-format", targets: 4 },
          ],
          order: [[4, "desc"]],
        })
        .columns.adjust();

      requests_table_filter_html = `
              <div class="col-sm-12 col-md-12 p-0">
                  <div id="user_requests_table_filter_approval_type" class="datatable_filter_approval_type">
                      <div style="display:flex;align-items:center;">
                          <h6 class="mb-0 mr-2">Approval Type:</h6>
                          <select id="request_approval_type_filter" style="border-radius:1.8rem">
                              <option value="">All</option>
                              <option value="New user group request">New user group request</option>
                              <option value="New group permission request">New group permission request</option>
                              <option value="New user request">New user request</option>
                              <option value="Delete user request">Delete user request</option>
                          </select>
                      </div>
                  </div>
              </div>`;

      $("#user_requests_table_wrapper")
        .find(".row")
        .eq(0)
        .addClass("mobile-column-reverse");
      $("#user_requests_table_wrapper")
        .find(".row")
        .eq(0)
        .append(requests_table_filter_html);

      $("#request_approval_type_filter").select2({
        width: "25%",
      });
      $("[name=user_requests_table_length]")
        .closest("label")
        .css("display", "flex");
      $("[name=user_requests_table_length]")
        .closest("label")
        .css("align-items", "center");
      $("[name=user_requests_table_length]").closest("label").css("gap", "9px");
      $("[name=user_requests_table_length]")
        .closest("label")
        .css("text-indent", "0");
      $("[name=user_requests_table_length]")
        .closest("label")
        .css("padding-left", "7.5px");
      $("[name=user_requests_table_length]").select2({
        width: "50%",
      });

      $("#user_requests_table_filter")
        .find("input[type=search]")
        .attr(
          "style",
          "border-radius: 1.8rem !important;border: 1px solid lightgrey !important;height: 28px;padding: 4px 9px;"
        );
      $("#user_requests_table_filter")
        .parent()
        .attr("class", "col-sm-12 col-md-12 col-lg-6");

      $("#request_approval_type_filter").on("change", function () {
        var selectedValue = $(this).val();
        if (selectedValue == "") {
          requests_table.column(1).search("");
          requests_table.column(1).draw();
        } else {
          requests_table.column(1).search("");
          requests_table.column(1).draw();
          requests_table
            .column(1)
            .search("^" + selectedValue + "$", true, false);
          requests_table.column(1).draw();
        }
      });

      $("#user_requests_table").on(
        "column-visibility.dt",
        function (e, settings, column, state) {
          $(`#` + "user_requests_table")
            .DataTable()
            .columns.adjust();
        }
      );
      $(document).on("shown.bs.modal", function (e) {
        $.fn.dataTable.tables({ visible: true, api: true }).columns.adjust();
      });

      $(".permission_button").on("click", approvePermissions);
      $(".userpermission_approve").on("click", userApproval);
      $(".userpermission_reject").on("click", userReject);
      $(".approve_button").on("click", groupApproval);
      $(".approve_ind").on("click", approve_ind);
      $(".reject_ind").on("click", reject_ind);
    },
    error: function () {
      Swal.fire({ icon: "error", text: "Error! Please try again." });
    },
  });
}

$(document).ready(function () {
  $("#user_range").daterangepicker({
    locale: {
      format: "YYYY-MM-DD",
    },
  });
});

function createUsers() {
  user_list = [];
  counter = 1;
  user_creation = $(".user_creation");
  var html_result = true
  var is_form_valid = false;
  for (element of user_creation) {
    obj = {};

    if (
      $(element).find("[name=username]").val() &&
      $(element).find("[name=password]").val() &&
      $(element).find("[name=email]").val()
    ) {
      obj["name"] = $(element).find("[name=username]").val();
      obj["password"] = $(element).find("[name=password]").val();
      obj["email"] = $(element).find("[name=email]").val();
      obj["a_type"] = $(element)
        .find(`[name=a_type__${counter}]:checked`)
        .val();
      obj["is_developer"] = $(element)
        .find("[name=is_developer]")
        .prop("checked");
      user_list.push(obj);
      is_form_valid = true;
    } else {
      if (counter == 1) {
        Swal.fire({
          icon: "warning",
          text: "Please enter all the details for atleast 1 user",
        });
        break;
      }
    }
    counter += 1;
  }
  var columns_list = ['name', 'password', 'email']
  for (let i in user_list){
    if (html_result){
      for (let j in columns_list){
      let check_html = /<|>/.test(user_list[i][columns_list[j]]);
        if (check_html){
            html_result = false
            break;
        }
      }
    }
  }

  if (!html_result){
    Swal.fire({
      icon: "error",
      text: "Unauthorised input. Please check and try again.",
    });
  }else{
    if (is_form_valid) {
      $.ajax({
        url: `/users/${app_code2}/${current_dev_mode2}/user_management/`,
        data: {
          user_list: JSON.stringify(user_list),
          operation: "user_creation",
        },
        dataType: "json",
        type: "POST",
        success: function (response) {
          developerMsg = response.DeveloperMsg;
          userMsg = response.UserMsg;
          SuccessMsg = response.SuccessMsg;
          reloadUserTable = response.sent_for_approval;

          devError = "";
          userError = "";
          success_msg = "";
          if (SuccessMsg.length > 0) {
            for (msg of SuccessMsg) {
              success_msg = `
                        <ul>
                            <li>${msg}</li>
                        </ul>
                        <br>
                        `;
            }
          }
          if (developerMsg.length > 0) {
            for (msg of developerMsg) {
              devError = `
                        <b>Developer Creation Errors</b>
                        <ul style="text-align:justify">
                            <li>${msg}</li>
                        </ul>
                        <br>
                        `;
            }
          }
          if (userMsg.length > 0) {
            userError = `
                        <b>User Creation Errors</b>
                        <ul style="text-align:justify">
                        `;
            for (msg of userMsg) {
              userError += `
                            <li>${msg}</li>
                        `;
            }
            userError += `</ul>
                        `;
          }

          final_html = "";
          if (devError || userError) {
            final_html = devError + userError;
            icon = "warning";
          } else {
            final_html = "User/s successfully sent for approval.";
            icon = "success";
          }
          $("#createNewUserModal").modal("hide");
          Swal.fire({ icon: icon, html: final_html });
          if (!reloadUserTable) {
            $("#userTable").DataTable().draw();
          }
        },
        error: function () {
          $("#createNewUserModal").modal("hide");
          Swal.fire({
            icon: "error",
            text: "Error! Failure in creating users. Please try again",
          });
        },
      });
    }
  }
}

function approve_all_permission() {
  let groupname = $("#permissionmodal_heading")
    .text()
    .replace("(User Group : ", "")
    .replace(")", "");
  let level = $("#permissionmodal_level").text();
  var app_code_approval = $(".approve_ind_permission")
    .eq(0)
    .attr("data-app_code");
  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/userpermissionapproval/`,
    data: {
      groupName: groupname,
      level: level,
      operation: "approve_all_permission",
      app_code: app_code_approval,
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      Swal.fire({
        icon: "info",
        text: "Approved successfully! Permissions for users are getting updated. Please check the Notifications bell for further updates.",
      });
      location.reload();
    },
    error: function () {
      Swal.fire({
        icon: "error",
        text: "Error! Failure in executing approvals. Please try again.",
      });
    },
  });
}
function reject_all_permission() {
  let groupname = $("#permissionmodal_heading").text().replace(": ", "");
  let level = $("#permissionmodal_level").text();
  var app_code_approval = $(".approve_ind_permission")
    .eq(0)
    .attr("data-app_code");
  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/userpermissionrejection/`,
    data: {
      groupName: groupname,
      perm_level: level,
      operation: "reject_all_permission",
      app_code: app_code_approval,
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      Swal.fire({ icon: "success", text: "Rejected approvals successfully" });
      location.reload();
    },
    error: function () {
      Swal.fire({
        icon: "error",
        text: "Error! Failure in executing rejection of approvals. Please try again.",
      });
    },
  });
}

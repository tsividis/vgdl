### Helper functions for TBRL analyses

library("colorspace")
library(cowplot)
library("dplyr")
library(EnvStats)
library(ggExtra)
library("ggplot2")
library(grid)
library(here)
library(plotrix)
library(plyr)
library(purrr)
library("RColorBrewer")
library("stats")
library(zoo)
library("zoom")
library(Bolstad)

remove_string_from_name = function(name){
  strings_to_remove = c('gvgai_variant','expt_variant','variant_expt', 'variant','gvgai', 'expt')
  for (i in 1:length(strings_to_remove)){
    string_to_remove = strings_to_remove[i]
    if (grepl(string_to_remove, name)){
      keep = substr(name, nchar(string_to_remove)+2, nchar(name))
      return(keep)
    }
    else{
      keep=name
    }
  }
  return(name)
}

create_rand_string <- function() {
  a <- do.call(paste0, replicate(1, sample(LETTERS, 1, TRUE), FALSE))
  paste0(a, sprintf("%04d", sample(9999, 1, TRUE)), sample(LETTERS, 1, TRUE))
}


load_full_human_data = function(){
  fullhumandata = list()
  for (humandatapath in humandatapaths){
    path = paste('~/Projects/atari/vgdl/humandata/',humandatapath, sep='')
    d=read.csv(path, header=TRUE, na.strings='NA')
    if (length(fullhumandata)==0){
      fullhumandata = d
    }
    else{
      fullhumandata = rbind(fullhumandata,d)
    }
  }
  fullhumandata$long_agent_type=as.factor('human')
  fullhumandata$agent_type=as.factor('human')
  fullhumandata$modelrun_ID = as.factor('oct29')
  fullhumandata$condition = as.factor('full')
  
  fullhumandata$game_name = as.factor(fullhumandata$game_name)
  fullhumandata = select(fullhumandata, -levels_lost, -group, -gameNumber, -gameRound)
  data = fullhumandata
  data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score')]

data$game_name = as.factor(as.character(lapply(as.vector(data$game_name), remove_string_from_name)))
return(data)
}


make_human_normed_data = function(dataframe){
  
  games_to_levels = data.frame(game_name=as.character(), num_levels=as.numeric())
  for (i in 1:length(levels(dataframe$game_name))){
    game_name=levels(dataframe$game_name)[i]
    num_levels = 5
    if ( (grepl('expt', game_name)) | (grepl('bees', game_name) )| (grepl('corridor',game_name))| 
         (grepl('closing',game_name)) ){
      num_levels=4
    }
    if ((grepl('expt_ee', game_name)) | (grepl('expt_preconditions_1', game_name)) ){
      num_levels=6
    }
    if (game_name %in% c('expt_preconditions', 'expt_preconditions_2')){
      num_levels=5
    }
    new = data.frame(game_name=game_name, num_levels=num_levels)
    games_to_levels = rbind(games_to_levels, new)
  }
  
  
  outputdata = data.frame(game_name=as.character(), agent_type=as.character(), max_score=as.numeric(), 
                            max_steps=as.numeric(), planning_time=as.numeric(), max_levels_won=as.numeric(),
                            level_num=as.numeric(), level_efficiency=as.numeric(), mean_planner_steps=as.numeric())
  
  for (j in 1:length(unique(dataframe$agent_type))){
    agent = unique(dataframe$agent_type)[j]
    print(agent)
    for (i in 1:length(unique(dataframe$game_name))){
      g = subset(dataframe, game_name==unique(dataframe$game_name)[i])
      # print(unique(dataframe$game_name)[i])
      s = subset(g, agent_type==agent)
      if (length(s$cumulative_steps)>0){
        ## grab each subject's max_steps and max_wins.
        level_maxes = list()
        cumulative_step_maxes = list()
        planner_step_maxes = list()
        idx=1
        for (k in 1:length(unique(s$subject_ID))){
          subject = unique(s$subject_ID)[k]
          subjectdata = s[which(s$subject_ID==subject),]
          if (length(subjectdata$cumulative_steps)>0){
            if(max(subjectdata$cumulative_steps)>0){
              level_maxes[[idx]] = max(subjectdata$cumulative_wins)
              cumulative_step_maxes[[idx]] = max(subjectdata$cumulative_steps)
              planner_step_maxes[[idx]] = max(subjectdata$cumulative_planner_nodes)
              idx = idx+1            
            }
            
          }
        }
        
        ## mean vector of win numbers
        mean_wins = mean(as.numeric(as.vector(level_maxes)))
        
        ##mean of vector steps_to_win ratios
        l_e = mean(as.numeric(as.vector(level_maxes))/as.numeric(as.vector(cumulative_step_maxes)))
        
        mean_planner_steps = mean(as.numeric(as.vector(planner_step_maxes)))
        
        ## the row we want
        r = subset(s, cumulative_steps==max(cumulative_steps))[1,]
        ## take only the relevant columns and put them in the new data frame
        new = data.frame(game_name=r$game_name, agent_type=r$agent_type, max_score=r$score, 
                         max_steps=r$cumulative_steps, mean_levels_won=mean_wins,
                         level_num=subset(games_to_levels, (game_name==r$game_name))$num_levels,
                         level_efficiency=l_e, mean_planner_steps=mean_planner_steps)
        outputdata = rbind(outputdata, new)
      }
    }
  }
  
  
  outputdata = mutate(outputdata, level_percentage = mean_levels_won/level_num)
  outputdata = mutate(outputdata, composite_ratio = level_percentage*level_efficiency)
  outputdata = mutate(outputdata, planning_normed_composite_ratio = composite_ratio/mean_planner_steps)
  
  outputdata$human_normed_composite_ratio=NA
  ##norm by human level_efficiency
  for (i in 1:length(unique(outputdata$game_name))){
    game = unique(outputdata$game_name)[i]
    human_composite_ratio = subset(outputdata, agent_type=='human' & game_name==game)$composite_ratio
    for (agent in unique(outputdata$agent_type)){
      row = outputdata[which(outputdata$agent_type==agent & outputdata$game_name==game),]
      outputdata[which(outputdata$agent_type==agent & outputdata$game_name==game),]$human_normed_composite_ratio = row$composite_ratio/human_composite_ratio
    }
  }
  
  for (i in 1:length(outputdata$human_normed_composite_ratio)){
    if (outputdata$human_normed_composite_ratio[i]==0){
      outputdata$human_normed_composite_ratio[i]=10e-8
    }
  }
  
  outputdata$formatted_game_name = NA
  for (i in 1:length(outputdata$game_name)){
    outputdata$formatted_game_name[i] = gsub('_', ' ', outputdata$game_name[i])
    if (outputdata$formatted_game_name[i]=='ee'){
      outputdata$formatted_game_name[i] = 'explore/exploit'
    }
    if (outputdata$formatted_game_name[i]=='ee 1'){
      outputdata$formatted_game_name[i] = 'explore/exploit 1'
    }
    if (outputdata$formatted_game_name[i]=='ee 2'){
      outputdata$formatted_game_name[i] = 'explore/exploit 2'
    }
    if (outputdata$formatted_game_name[i]=='ee 3'){
      outputdata$formatted_game_name[i] = 'explore/exploit 3'
    }
  }
  agent_types = unique(outputdata$agent_type)
  outputdata$model_cluster = 'none'
  if ('EMPA' %in% agent_types){
    outputdata[outputdata$agent_type=='EMPA',]$model_cluster = 'EMPA'
  }
  if ('e-greedy 1k DS' %in% agent_types | 'e-greedy 2k DS' %in% agent_types |
      'e-greedy 1k' %in% agent_types | 'e-greedy 1k' %in% agent_types){
    outputdata[outputdata$agent_type%in%c('e-greedy 1k DS', 'e-greedy 2k DS', 'e-greedy 1k', 'e-greedy 2k'),]$model_cluster = 'Exploration ablations'
  }
  if ('no goal gradient' %in% agent_types | 'no subgoals' %in% agent_types | 'no subgoals + no gradient' %in% agent_types |
      'no IW' %in% agent_types | 'no subgoals + no gradient + no IW' %in% agent_types){
    outputdata[outputdata$agent_type%in%c('no goal gradient', 'no subgoals',  'no subgoals + no gradient',
                                          'no IW', 'no subgoals + no gradient + no IW'),]$model_cluster = 'Planner ablations'
  }
  if ('DDQN 1k' %in% agent_types | 'DDQN 10k' %in% agent_types | 'DDQN 100k' %in% agent_types){
    outputdata[outputdata$agent_type%in%c('DDQN 1k', 'DDQN 10k', 'DDQN 100k'),]$model_cluster = 'Deep RL'
  }
  if ('rainbow 50k' %in% agent_types | 'rainbow 150k' %in% agent_types | 'rainbow 250k' %in% agent_types |
      'rainbow' %in% agent_types){
    outputdata[outputdata$agent_type%in%c('rainbow 50k', 'rainbow 150k', 'rainbow 250k','rainbow'),]$model_cluster = 'Deep RL'
  }
  # outputdata[outputdata$agent_type=='random',]$model_cluster = 'Random'
  outputdata = transform(outputdata, model_cluster=factor(model_cluster, levels=c('EMPA', 'Exploration ablations', 'Planner ablations', 'Deep RL','Random', NA)))
  
  return(outputdata)
}

make_scatter_data = function(human_normed_data){
  output = data.frame(game_name=as.character(), empa_score=as.numeric(), model_score=as.numeric(), 
                      empa_steps=as.numeric(), model_steps=as.numeric(),
                      empa_levels=as.numeric(), model_levels=as.numeric(),
                      empa_planning_steps=as.numeric(), model_planning_steps=as.numeric(),
                      empa_planning_efficiency=as.numeric(), model_planning_efficiency=as.numeric(),
                      model_name=as.character(), model_cluster=as.character())
  models = unique(human_normed_data$agent_type)
  for (game in unique(human_normed_data$game_name)){
    print(game)
    s = subset(human_normed_data, game_name == game)
    empa_score_on_game = filter(s, agent_type=='EMPA')$composite_ratio
    empa_steps_on_game = filter(s, agent_type=='EMPA')$max_steps
    empa_levels_on_game = filter(s, agent_type=='EMPA')$mean_levels_won
    empa_planning_steps_on_game = filter(s, agent_type=='EMPA')$mean_planner_steps
    empa_planning_efficiency_on_game = filter(s, agent_type=='EMPA')$planning_normed_composite_ratio
    
    for (model in models){
      model_row = filter(s, agent_type==model)
      if (nrow(model_row)>0){
      model_score_on_game = model_row$composite_ratio
      model_steps_on_game = model_row$max_steps
      model_levels_on_game = model_row$mean_levels_won
      model_planning_steps_on_game = model_row$mean_planner_steps
      model_planning_efficiency_on_game = model_row$planning_normed_composite_ratio
      model_cluster = model_row$model_cluster
      if (!(model%in%c('EMPA','human','DDQN 1k', 'DDQN 10k'))){
        row = data.frame(game_name=game, empa_score=empa_score_on_game, model_score=model_score_on_game,
                         empa_steps=empa_steps_on_game, model_steps=model_steps_on_game,
                         empa_levels=empa_levels_on_game, model_levels=model_levels_on_game,
                         empa_planning_steps=empa_planning_steps_on_game, model_planning_steps=model_planning_steps_on_game,
                         empa_planning_efficiency = empa_planning_efficiency_on_game, model_planning_efficiency = model_planning_efficiency_on_game,
                         model_name=model, model_cluster=model_cluster)
        output = rbind(output, row)
      }
    }}
  }
  output$model_name = ordered(output$model_name, levels=c("e-greedy 1k", "e-greedy 2k", 
                                                          "e-greedy 1k DS", "e-greedy 2k DS",
                                                          "no goal gradient", "no subgoals",
                                                          "no subgoals + no gradient",
                                                          "no IW", "no subgoals + no gradient + no IW",
                                                          "DDQN 100k", "rainbow 150k", "random policy"))
  output$model_cluster = ordered(output$model_cluster, levels = c('EMPA', 'Exploration ablations', 'Planner ablations', 'Deep RL'))
  
  for (i in 1:length(output$empa_score)){
    if (output$empa_score[i]==0){
      output$empa_score[i]=1e-9
    }
    if (output$model_score[i]==0){
      output$model_score[i]=1e-9
    }
  }
  return(output)
}

load_reward_data = function(data_to_load, dates_or_groups){
  if (data_to_load=='EMPA'){
    data = c()
    for (date in dates_or_groups){
      path = paste(getwd(),'/data_files/EMPA/', date,'/csv_data/merged_data',sep='')
      # path = paste('~/Projects/atari/vgdl_data_files/',date, '/csv_data/merged_data', sep='')
      d=read.csv(path, header=TRUE, na.strings='NA')
      

      
      if(length(data)==0){
        data = d
      }
      else{
        for(colname in names(d)){
          if (!(colname %in% names(data))){
            data[,colname] = NA
          }
        }
        for(colname in names(data)){
          if(!(colname %in% names(d))){
            d[,colname]=NA
          }
        }
        data = rbind(data,d)
      }
    }
    data$modelrun_ID = as.factor(data$modelrun_ID)
    data$cumulative_steps = as.numeric(as.character(data$cumulative_timestep))
    data$long_agent_type = as.factor(data$agent_type)
    
    newdata = data.frame()
    
    ## remove batchIDs so you can use grepl easily in the next part
    for (agent in unique(data$agent_type)){
      agent_data = filter(data, agent_type==agent)
      loc = regexpr('_batchID',agent)[1]
      if (loc>0){
        new_agent_type = substr(agent, 0, loc-1)
        agent_data$long_agent_type = new_agent_type
        agent_data$agent_type = new_agent_type
      }
      newdata = rbind(newdata, agent_data)
    }
    data = newdata
    
    e_greedy_05='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_sTE=1000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
    e_greedy_1a='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_fe=0.1_sTE=1000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
    e_greedy_1a1='rand=False_eG=True_egv=N_fe=0.1_sTE=1000'
    e_greedy_1b='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_fe=0.1_sTE=2000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
    e_greedy_2a='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=DSDF_fe=0.1_sTE=1000_hyb=False_nnon=550_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
    e_greedy_2a1='rand=False_eG=True_egv=DSDF_fe=0.1_sTE=1000'
    e_greedy_2b='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=DSDF_fe=0.1_sTE=2000_hyb=False_nnon=550_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
    e_greedy_2b1='rand=False_eG=True_egv=DSDF_fe=0.1_sTE=2000'
    planner_AGH1a='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=AGH1_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
    planner_AGH1b='IW=1_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=AGH1_DTL=[]_IL=[]_ILR=[]_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
    planner_AGH1c='eG=False_PL=AGH1'
    planner_AGH2a='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=AGH2_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
    planner_AGH2b='IW=1_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=AGH2_DTL=[]_IL=[]_ILR=[]_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
    planner_AGH2c='eG=False_PL=AGH2'
    planner_AGH3a='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=AGH3_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
    planner_AGH3b='IW=1_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=AGH3_DTL=[]_IL=[]_ILR=[]_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
    planner_AGH3c='eG=False_PL=AGH3'
    planner_IWa='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=IW_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
    planner_IWb='IW=1_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=IW_DTL=[]_IL=[]_ILR=[]_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
    planner_IWc='eG=False_PL=IW'
    planner_IW_AGH3a='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=IW+AGH3_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
    planner_IW_AGH3b='IW=1_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=IW-AGH3_DTL=[]_IL=[]_ILR=[]_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
    planner_IW_AGH3c='eG=False_PL=IW-AGH3'
    
    IW2_e_greedy_1='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_sTE=2000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
    IW2_e_greedy_2='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_sTE=1000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
    IW2_e_greedy_3='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=DSDF_sTE=1000_hyb=False_nnon=550_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
    IW2_e_greedy_4='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=DSDF_sTE=2000_hyb=False_nnon=550_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
    
    data$agent_type = NA
    if (e_greedy_1a %in% unique(data$long_agent_type)){
      data[data$long_agent_type==e_greedy_1a,]$agent_type = 'e-greedy 1k'
    }
    if (e_greedy_1b %in% unique(data$long_agent_type)){
      data[data$long_agent_type==e_greedy_1b,]$agent_type = 'e-greedy 2k'
    }
    if (e_greedy_2a %in% unique(data$long_agent_type)){
      data[data$long_agent_type==e_greedy_2a,]$agent_type = 'e-greedy 1k DS'
    }
    if (e_greedy_2b %in% unique(data$long_agent_type)){
      data[data$long_agent_type==e_greedy_2b,]$agent_type = 'e-greedy 2k DS'
    }
    if (e_greedy_05 %in% unique(data$long_agent_type)){
      data[data$long_agent_type==e_greedy_05,]$agent_type = 'e-greedy .05'
    }
    if (planner_AGH1a %in% unique(data$long_agent_type)){
      data[data$long_agent_type==planner_AGH1a,]$agent_type = 'no goal gradient'
    }
    if (planner_AGH2a %in% unique(data$long_agent_type)){
      data[data$long_agent_type==planner_AGH2a,]$agent_type = 'no subgoals'
    }
    if (planner_AGH3a %in% unique(data$long_agent_type)){
      data[data$long_agent_type==planner_AGH3a,]$agent_type = 'no subgoals + no gradient'
    }
    if (planner_IWa %in% unique(data$long_agent_type)){
      data[data$long_agent_type==planner_IWa,]$agent_type = 'no IW'
    }
    if (planner_IW_AGH3a %in% unique(data$long_agent_type)){
      data[data$long_agent_type==planner_IW_AGH3a,]$agent_type = 'no subgoals + no gradient + no IW'
    }
    
    ## longer newer planner IDs:
    if (planner_AGH1b %in% unique(data$long_agent_type)){
      data[data$long_agent_type==planner_AGH1b,]$agent_type = 'no goal gradient'
    }
    if (planner_AGH2b %in% unique(data$long_agent_type)){
      data[data$long_agent_type==planner_AGH2b,]$agent_type = 'no subgoals'
    }
    if (planner_AGH3b %in% unique(data$long_agent_type)){
      data[data$long_agent_type==planner_AGH3b,]$agent_type = 'no subgoals + no gradient'
    }
    if (planner_IWb %in% unique(data$long_agent_type)){
      data[data$long_agent_type==planner_IWb,]$agent_type = 'no IW'
    }
    if (planner_IW_AGH3b %in% unique(data$long_agent_type)){
      data[data$long_agent_type==planner_IW_AGH3b,]$agent_type = 'no subgoals + no gradient + no IW'
    }
    
    ## shortest, newest planner IDs
    if (e_greedy_1a1 %in% unique(data$long_agent_type)){
      data[data$long_agent_type==e_greedy_1a1,]$agent_type = 'e-greedy 1k'
    }
    if (e_greedy_2a1 %in% unique(data$long_agent_type)){
      data[data$long_agent_type==e_greedy_2a1,]$agent_type = 'e-greedy 1k DS'
    }
    if (e_greedy_2b1 %in% unique(data$long_agent_type)){
      data[data$long_agent_type==e_greedy_2b1,]$agent_type = 'e-greedy 2k DS'
    }
    if ('rand=False_eG=False_egv=SS_fe=0.1_sTE=1000' %in% unique(data$long_agent_type)){
      data[data$long_agent_type=='rand=False_eG=False_egv=SS_fe=0.1_sTE=1000',]$agent_type = 'e-greedy 1k SS'
    }
    if ('rand=False_eG=False_egv=SN_fe=0.1_sTE=1000' %in% unique(data$long_agent_type)){
      data[data$long_agent_type=='rand=False_eG=False_egv=SN_fe=0.1_sTE=1000',]$agent_type = 'e-greedy 1k SN'
    }
    if (planner_AGH1c %in% unique(data$long_agent_type)){
      data[data$long_agent_type==planner_AGH1c,]$agent_type = 'no goal gradient'
    }
    if (planner_AGH2c %in% unique(data$long_agent_type)){
      data[data$long_agent_type==planner_AGH2c,]$agent_type = 'no subgoals'
    }
    if (planner_AGH3c %in% unique(data$long_agent_type)){
      data[data$long_agent_type==planner_AGH3c,]$agent_type = 'no subgoals + no gradient'
    }
    if (planner_IWc %in% unique(data$long_agent_type)){
      data[data$long_agent_type==planner_IWc,]$agent_type = 'no IW'
    }
    if (planner_IW_AGH3c %in% unique(data$long_agent_type)){
      data[data$long_agent_type==planner_IW_AGH3c,]$agent_type = 'no subgoals + no gradient + no IW'
    }
    ## old IW models we don't want
    if (IW2_e_greedy_1 %in% unique(data$long_agent_type)){
      data[data$long_agent_type==IW2_e_greedy_1,]$agent_type = 'IW2 e-greedy. IGNORE.'
    }
    if (IW2_e_greedy_2 %in% unique(data$long_agent_type)){
      data[data$long_agent_type==IW2_e_greedy_2,]$agent_type = 'IW2 e-greedy. IGNORE.'
    }
    if (IW2_e_greedy_3 %in% unique(data$long_agent_type)){
      data[data$long_agent_type==IW2_e_greedy_3,]$agent_type = 'IW2 e-greedy. IGNORE.'
    }
    if (IW2_e_greedy_4 %in% unique(data$long_agent_type)){
      data[data$long_agent_type==IW2_e_greedy_4,]$agent_type = 'IW2 e-greedy. IGNORE.'
    }
    for (agent in unique(data$long_agent_type)){
      if (grepl('rand=True', agent)){
        data[grepl('rand=True', data$long_agent_type),]$agent_type = 'random policy'
      }
    }
    if (NA %in% unique(data$agent_type)){
      data[is.na(data$agent_type),]$agent_type = 'EMPA'
    }
    
    data$score = as.numeric(as.character(data$sparse_score))
    data = select(data, -timestep, -level_max_score, -cumulative_max_score, -sparse_score, -level_accumulated_score, 
                  -episode_end, -win, -planner_nodes, -planner_settings,# -cumulative_planner_nodes, 
                  -cumulative_timestep, condition, -exploration_burn_ins)
    if ('entropy'%in% names(data)){
      data = select(data, -entropy)
    }
    if ('time_elapsed'%in%names(data)){
      data = select(data, -time_elapsed)
    }
    if ('sparse_levels_won'%in%names(data)){
      data = select(data, -sparse_levels_won)
    }
    data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score', 'cumulative_planner_nodes')]
  }else if (data_to_load == 'DDQN'){
    dqndata = list()
    for (gamefile in list.files(ddqn_path)){
      filename = paste(ddqn_path,'/',gamefile,sep='')
      if(grepl('ddqn/', filename)){
        gamenamestart = unlist(gregexpr('ddqn/',filename))+nchar('ddqn/')
        gamenameend = unlist(gregexpr('_DDQN_reward', filename))-1 ##careful; you changed this 8/23/19. used to be +1.
        }
      game = substr(filename, gamenamestart, gamenameend)
      if (grepl('k_', filename)){
        subject_ID_start = unlist(gregexpr('k_',filename))+2
        subject_ID_end = unlist(gregexpr('.csv', filename))-1 ##careful; you changed this 8/23/19. used to be +1.
        subject_ID = substr(filename, subject_ID_start, subject_ID_end)
      }else{
        subject_ID = create_rand_string()
      }
      d=read.csv(filename, header=TRUE, na.strings='NA')
      
      d$score = d$ep_reward
      d$game_name = as.factor(remove_string_from_name(game))
      d$cumulative_steps = d$steps
      d$subject_ID = as.factor(subject_ID)
      
      if ((grepl('101', filename) || grepl('trial1', filename) || grepl('decay1k', filename))){
        d$agent_type = as.factor("DDQN 1k") ## refers to the eps_decay (epsilon-greedy annealing) parameter in the DDQN implementation. 
      }else if ((grepl('102', filename)|| grepl('trial2', filename) || grepl('decay10k', filename))){
        d$agent_type = as.factor("DDQN 10k")
      }else if ((grepl('103', filename)||grepl('trial3', filename) || grepl('decay100k', filename))){
        d$agent_type = as.factor("DDQN 100k")
      }else{
        d$agent_type = as.factor("DDQN")
      }
      d$long_agent_type = d$agent_type
      d$cumulative_wins = as.numeric(0)
      for (i in 2:length(d$level)){
        if ((d$level[i]>d$level[i-1]) |(i==length(d$level)& (d$win[i]=='True'))){
          d$cumulative_wins[i] = d$cumulative_wins[i-1]+1
          # d$sparse_levels_won[i] = d$cumulative_wins[i]
        }
        else{
          d$cumulative_wins[i] = d$cumulative_wins[i-1]
        }
      }
      d$level_number = d$level
      
      dqndata = rbind(dqndata,d)
    }
    data = dqndata
    data$modelrun_ID = NA
    data$cumulative_planner_nodes = NA
    data = select(data, -criteria, -level, -ep_reward)
    data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score', 'cumulative_planner_nodes')]
    
  }else if (data_to_load == 'rainbow'){
    rainbowdata = list()
    for (gamefile in list.files(rainbow_path)){
      filename = paste(rainbow_path,'/', gamefile,sep='')
      if(grepl('rainbow/', filename)){
        # gamenamestart = unlist(gregexpr('rainbow/',filename))+nchar('rainbow/')
        # gamenameend = unlist(gregexpr('_reward', filename))+1        
        gamenamestart = unlist(gregexpr('rainbow/',filename))+nchar('rainbow/')
        gamenameend = unlist(gregexpr('_reward', filename))-1
      }
      
      game = substr(filename, gamenamestart, gamenameend)
      if (grepl('k_', filename)){
        subject_ID_start = unlist(gregexpr('k_',filename))+2
        subject_ID_end = unlist(gregexpr('.csv', filename))+1
        subject_ID = substr(filename, subject_ID_start, subject_ID_end)
      }else{
        subject_ID = create_rand_string()
      }
      d=read.csv(filename, header=TRUE, na.strings='NA')
      
      d$score = d$ep_reward
      d$game_name = as.factor(remove_string_from_name(game))
      d$cumulative_steps = d$steps
      d$subject_ID = as.factor(subject_ID)
      
      d$agent_type = as.factor("rainbow 150k")

      d$long_agent_type = d$agent_type
      d$cumulative_wins = as.numeric(0)
      if(length(d$level>2)){
        for (i in 2:length(d$level)){
          if ((d$level[i]>d$level[i-1]) |(i==length(d$level)& (d$win[i]=='True'))){
            d$cumulative_wins[i] = d$cumulative_wins[i-1]+1
            # d$sparse_levels_won[i] = d$cumulative_wins[i]
          }
          else{
            d$cumulative_wins[i] = d$cumulative_wins[i-1]
          }
        }}
      d$level_number = d$level
      rainbowdata = rbind(rainbowdata,d)
    }
    data = rainbowdata
    data$modelrun_ID = NA
    data$cumulative_planner_nodes = NA
    data = select(data, -criteria, -level, -ep_reward)
    data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score', 'cumulative_planner_nodes')]
  }else if (data_to_load == 'random'){
    randomdata = list()
    for (gamefile in list.files(random_path)){
      filename = paste(random_path,gamefile,sep='')
      if (grepl('randomdata/', filename)){
        gamenamestart = unlist(gregexpr('randomdata/',filename))+nchar('randomdata/')
        gamenameend = unlist(gregexpr('_reward', filename))-1
      }
      
      game = substr(filename, gamenamestart, gamenameend)
      print(game)
      if (grepl('k_', filename)){
        subject_ID_start = unlist(gregexpr('k_',filename))+2
        subject_ID_end = unlist(gregexpr('.csv', filename))+1
        subject_ID = substr(filename, subject_ID_start, subject_ID_end)
      }else{
        subject_ID = create_rand_string()
      }
      d=read.csv(filename, header=TRUE, na.strings='NA')
      
      d$score = d$ep_reward
      d$game_name = as.factor(remove_string_from_name(game))
      d$cumulative_steps = d$steps
      d$subject_ID = as.factor(subject_ID)
      d$agent_type = 'random'
      d$long_agent_type = d$agent_type
      d$cumulative_wins = as.numeric(0)
      if(length(d$level>2)){
        for (i in 2:length(d$level)){
          if ((d$level[i]>d$level[i-1]) |(i==length(d$level)& (d$win[i]=='True'))){
            d$cumulative_wins[i] = d$cumulative_wins[i-1]+1
            # d$sparse_levels_won[i] = d$cumulative_wins[i]
          }
          else{
            d$cumulative_wins[i] = d$cumulative_wins[i-1]
          }
        }}
      d$level_number = d$level
      
      randomdata = rbind(randomdata,d)
    }
    data = randomdata
    data$modelrun_ID = NA
    data$cumulative_planner_nodes = NA
    data = select(data, -criteria, -level, -ep_reward)
    data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score', 'cumulative_planner_nodes')]
  }
  else if (data_to_load == 'human'){
    humandata = list()
    for (humandatapath in humandatapaths){
      path = paste(getwd(), '/data_files/humandata/',humandatapath, sep='')
      d=read.csv(path, header=TRUE, na.strings='NA')
      if (length(humandata)==0){
        humandata = d
      }
      else{
        humandata = rbind(humandata,d)
      }
    }
    humandata$long_agent_type=as.factor('human')
    humandata$agent_type=as.factor('human')
    humandata$modelrun_ID = as.factor('oct29')
    humandata$condition = as.factor('full')
    
    humandata$game_name = as.factor(humandata$game_name)
    # humandata$cumulative_steps = humandata$cumulative_frames ## if you want to look at game frames
    humandata = select(humandata, -levels_lost, -group, -gameNumber, -gameRound)
    humandata$cumulative_planner_nodes = NA
    data = humandata
    data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score','cumulative_planner_nodes')]
  }
  
  data$game_name = as.factor(as.character(lapply(as.vector(data$game_name), remove_string_from_name)))
  
  
  return (data)
}

synthetic_games = c('antagonist', 'bees_and_birds', 'bees and birds', 'closing_gates', 'closing gates', 'corridor', 'ee', 
                    'helper', 'preconditions', 'push_boulders','push boulders', 'relational', 'surprise')


##GVGAI-original, GVGAI-variant, synthetic-original, synthetic-variant
game_category_df = data.frame(game_name = as.character(), category = as.character(), gvgai_or_synthetic = as.character(), human_normed_composite_ratio = as.numeric())

for (game in unique(human_normed_data$game_name)){
  gvgai_or_synthetic = 'GVGAI'
  for (synthetic_name in synthetic_games){
    if (grepl(synthetic_name, game)){
      gvgai_or_synthetic = 'Synthetic'
    }
  }
  original_or_variant = 'original'
  for (num in c('1', '2', '3', '4')){
    if (grepl(num, game)){
      original_or_variant = 'variant'
    }
  }
  game_category = paste(gvgai_or_synthetic, '_', original_or_variant)
  hncr = filter(human_normed_data, game_name==game, agent_type=='EMPA')$human_normed_composite_ratio
  row = data.frame(game_name = game, category = game_category, gvgai_or_synthetic = gvgai_or_synthetic, human_normed_composite_ratio=hncr)
  game_category_df = rbind(game_category_df, row)
}


game_category_scatter = data.frame(game_name = as.character(), category = as.character(), gvgai_or_synthetic = as.character(), 
                              human_score = as.numeric(), empa_score = as.numeric())

for (game in unique(human_normed_data$game_name)){
  gvgai_or_synthetic = 'GVGAI'
  for (synthetic_name in synthetic_games){
    if (grepl(synthetic_name, game)){
      gvgai_or_synthetic = 'Synthetic'
    }
  }
  original_or_variant = 'original'
  for (num in c('1', '2', '3', '4')){
    if (grepl(num, game)){
      original_or_variant = 'variant'
    }
  }
  game_category = paste(gvgai_or_synthetic, '_', original_or_variant)
  human_score = filter(human_normed_data, game_name==game, agent_type=='human')$composite_ratio
  empa_score = filter(human_normed_data, game_name==game, agent_type=='EMPA')$composite_ratio
  row = data.frame(game_name = game, category = game_category, gvgai_or_synthetic = gvgai_or_synthetic, 
                   human_score = human_score, empa_score = empa_score)
  game_category_scatter = rbind(game_category_scatter, row)
}

## recalculate using kappas
game_category_scatter2 = data.frame(game_name = as.character(), category = as.character(), gvgai_or_synthetic = as.character(), 
                                   human_score = as.numeric(), empa_score = as.numeric())

for (game in unique(kappadata$game_name)){
  gvgai_or_synthetic = 'GVGAI'
  for (synthetic_name in synthetic_games){
    if (grepl(synthetic_name, game)){
      gvgai_or_synthetic = 'Synthetic'
    }
  }
  original_or_variant = 'original'
  for (num in c('1', '2', '3', '4')){
    if (grepl(num, game)){
      original_or_variant = 'variant'
    }
  }
  game_category = paste(gvgai_or_synthetic, '_', original_or_variant)
  human_score = mean(filter(kappadata, game_name==game, agent_type=='human')$kappa)
  empa_score = mean(filter(kappadata, game_name==game, agent_type=='EMPA')$kappa)
  row = data.frame(game_name = game, category = game_category, gvgai_or_synthetic = gvgai_or_synthetic, 
                   human_score = human_score, empa_score = empa_score)
  game_category_scatter2 = rbind(game_category_scatter2, row)
}


load_ratings = function(){
  path = paste(getwd(),'/data_files/humandata_ratings/ratings', sep='')
  ratingpaths = list.files(path)
  ratings = list()
  for (rating in ratingpaths){
    ratingpath = paste(path, '/', rating, sep='')
    r=read.csv(ratingpath, header=TRUE, na.strings='NA')
    if (length(ratings)==0){
      ratings = r
    }
    else{
      ratings = rbind(ratings,r)
    }
  }
  substrRight <- function(x, n){
    substr(x, nchar(x)-n+1, nchar(x))
  }
  find_source_game = function(name){
    if (substrRight(name,1)%in%c("1","2","3","4")){
      return(substr(name,0,nchar(name)-2))
    }
    else{
      return(name)}
  }
  find_variant_number = function(name){
    lastchar = substrRight(name,1)
    if (lastchar%in%c("1","2","3","4")){
      return(lastchar)
    }
    else{
      return('0')
    }
  }
  ratings$game_name = as.factor(ratings$gameName)
  ratings$source_game_name = as.factor(as.character(lapply(as.vector(ratings$game_name), find_source_game)))
  ratings$variant_number = as.factor(as.character(lapply(as.vector(ratings$game_name), find_variant_number)))
  for (i in 1:length(ratings$difficulty)){
    if (!is.na(ratings$difficulty[i]) & ratings$difficulty[i]=="None"){
      ratings$difficulty[i]=NA
    }
    if (ratings$interestingness[i]=="None"){
      ratings$interestingness[i]=NA
    }
  }
  ratings$difficulty = as.numeric(ratings$difficulty)
  ratings$interestingness = as.numeric(ratings$interestingness)
  ## you also have enjoyability
  
  return(ratings)  
}



## Gives count, mean, standard deviation, standard error of the mean, and confidence interval (default 95%).
##   data: a data frame.
##   measurevar: the name of a column that contains the variable to be summariezed
##   groupvars: a vector containing names of columns that contain grouping variables
##   na.rm: a boolean that indicates whether to ignore NA's
##   conf.interval: the percent range of the confidence interval (default is 95%)
summarySE <- function(data=NULL, measurevar, groupvars=NULL, na.rm=FALSE,
                      conf.interval=.95, .drop=TRUE) {
  library(plyr)
  
  # New version of length which can handle NA's: if na.rm==T, don't count them
  length2 <- function (x, na.rm=FALSE) {
    if (na.rm) sum(!is.na(x))
    else       length(x)
  }
  
  # This does the summary. For each group's data frame, return a vector with
  # N, mean, and sd
  datac <- ddply(data, groupvars, .drop=.drop,
                 .fun = function(xx, col) {
                   c(N    = length2(xx[[col]], na.rm=na.rm),
                     mean = mean   (xx[[col]], na.rm=na.rm),
                     sd   = sd     (xx[[col]], na.rm=na.rm)
                   )
                 },
                 measurevar
  )
  
  # Rename the "mean" column    
  # datac$measurevar = datac$mean
  colnames(datac)[colnames(datac)=="mean"] <- measurevar
  
  datac$se <- datac$sd / sqrt(datac$N)  # Calculate standard error of the mean
  
  # Confidence interval multiplier for standard error
  # Calculate t-statistic for confidence interval: 
  # e.g., if conf.interval is .95, use .975 (above/below), and use df=N-1
  ciMult <- qt(conf.interval/2 + .5, datac$N-1)
  datac$ci <- datac$se * ciMult
  
  return(datac)
}

calculate_kappa = function(subject_data, step_minimum){
  game = subject_data$game_name[1]
  if (game %in% c('antagonist', 'antagonist_1', 'antagonist_2', 'bees_and_birds', 'bees_and_birds_1', 
                  'closing_gates', 'closing_gates_1', 'corridor', 'corridor_1', 
                  'helper', 'helper_1', 'helper_2',
                  'push_boulders', 'push_boulders_1', 'push_boulders_2', 'relational', 'relational_1', 'relational_2')){
    level_max = 4
  }else if (game %in% c('ee', 'ee_1', 'ee_2', 'ee_3', 'preconditions_1')){
    level_max = 6
  }else{
    level_max = 5
  }
  
  last_row = subject_data[length(subject_data$cumulative_steps),]
  
  if (last_row$cumulative_steps != 0){
    kappa = (last_row$level_number/level_max)*(last_row$level_number/last_row$cumulative_steps)
    if(kappa==0){
      kappa=1e-7
    }
  }
  else{
    kappa = NA
  }
  
  if (!is.na(step_minimum)){
    if(last_row$cumulative_steps<step_minimum & last_row$level_number<3){
      kappa = NA
    }
  }
  return(kappa)
}


calculate_kappas = function(dataframe, step_minimum){
  ## make data structure for looking at levels_won for different planner settings (corresponding to runs on different days)
  kappadata = data.frame(game_name=as.character(), agent_type=as.character(), subject_ID=as.character(), kappa=as.numeric())
  
  for (agent in unique(dataframe$agent_type)){
    agent_games = filter(dataframe, agent_type==agent)
    for (game in unique(agent_games$game_name)){
      formatted_game_name = gsub('_', ' ', game)
      if (game=='ee'){
        formatted_game_name== 'explore/exploit'
      }
      if (game=='ee 1'){
        formatted_game_name== 'explore/exploit 1'
      }
      if (game=='ee 2'){
        formatted_game_name== 'explore/exploit 2'
      }
      if (game=='ee 3'){
        formatted_game_name== 'explore/exploit 3'
      }
      g = filter(agent_games, game_name==game)
      for (subject in unique(g$subject_ID)){
        d = filter(g, subject_ID==subject)
        kappa_score = calculate_kappa(d,step_minimum)
        ## Exclude the few subjects who logged in but didn't seem to play (cumulative_steps == 0)
        if (!is.na(kappa_score)){
          row = data.frame(game_name=formatted_game_name, agent_type=agent, subject_ID=subject, kappa=kappa_score)
          kappadata = rbind(kappadata, row)
        }
        
      }
    }
  }
  return(kappadata)
}

bootstrap_kappa_ratio = function(data1, data2){
  
  if(data1$game_name[1]%in%c('jaws 2', 'sokoban')){
    data1_samples = data1 ##edge effect adjustment for two games with <3 successes out of 10 runs.
    
  }else{
    data1_samples = sample_n(data1,length(data1$kappa),replace=TRUE)
  }
  
  data2_samples = sample_n(data2,length(data2$kappa),replace=TRUE)
  kappa_ratio = mean(data1_samples$kappa)/mean(data2_samples$kappa)
  
  return(kappa_ratio)
}

calculate_CI = function(x){
  x = x[is.finite(x)] ## remove Inf
  mu = mean(x)
  low_high = quantile(x, c(.025,.975))
  return(c(low_high[1], mu, low_high[2]))
}

bootstrap_means_and_CIs = function(kappadata, data1_type){
  ## Bootstrap 10k samples
  N=10
  M=10
  means_and_CIs = data.frame(game_name=as.character(), agent_type=as.character(), mean=as.numeric(), low_margin=as.numeric(), high_margin=as.numeric())
  for (game in unique(kappadata$game_name)){
    
    data1 = filter(kappadata, agent_type==data1_type, game_name==game, !is.na(kappa))
    data2 = filter(kappadata, agent_type=='human', game_name==game, !is.na(kappa))
    kappa_ratios = numeric(N)
    all_kappa_ratios = data.frame(values=as.numeric())
    ## double loop for speedup?
    for (j in 1:M){
      for (i in 1:N){
        kappas = bootstrap_kappa_ratio(data1, data2)
        kappa_ratios[i] = kappas
      }
      all_kappa_ratios = rbind(all_kappa_ratios, data.frame(values=kappa_ratios))
    }
    low_mean_high = calculate_CI(all_kappa_ratios$values)
    
    ## failure for models counts as 1e-7
    if(low_mean_high[2]==0){
      low_mean_high = c(1e-7, 1e-7, 1e-7)
    }  
    
    
    row = data.frame(game_name=game, agent_type='EMPA', mean=low_mean_high[2], low_margin=low_mean_high[1], high_margin=low_mean_high[3])
    means_and_CIs = rbind(means_and_CIs, row)
  }
  means_and_CIs = transform(means_and_CIs, agent_type=factor(agent_type, levels=c(data1_type, paste(data1_type, ' fail', sep=''))))
  
  return(means_and_CIs)
}



load_interaction_data = function(data_to_load, dates_or_groups){
  data = list()
  for (date_or_group in dates_or_groups){
    if (data_to_load == 'EMPA'){
      filename = paste(getwd(),'/data_files/EMPA/', date_or_group,'/csv_data/interaction_data', sep='')
      # filename = paste('~/Projects/atari/vgdl/',date_or_group, '/csv_data/interaction_data', sep='')
    }else if (data_to_load == 'human'){
      filename = paste(getwd(),'/data_files/human_interaction_data/', date_or_group, sep='')
      # filename = paste('~/Projects/atari/vgdl/vgdl/human_interaction_data/', date_or_group, sep='')
    }else if (data_to_load == 'DDQN'){
      filename = paste(ddqn_interaction_path, '/', date_or_group, sep='')
    }
    
    d=read.csv(filename, header=TRUE, na.strings='NA')
    
    if (data_to_load=='DDQN' & grepl('100k', date_or_group)){
      d$agent_type = 'DDQN 100k'
    }else if (data_to_load=='DDQN' & grepl('10k', date_or_group)){
      d$agent_type = 'DDQN 10k'
    }else if (data_to_load=='DDQN' & grepl('1k', date_or_group)){
      d$agent_type = 'DDQN 1k'
    }else{
      hi='hi'
    }
    if (data_to_load=='DDQN' & grepl('seed', date_or_group)){
      start = unlist(gregexpr('seed', date_or_group))
      stop = start+nchar('seed')
      d$subject_ID = substring(date_or_group, start, stop)
    }
    
    if(length(data)==0){
      data = d
    }else{
      for(colname in names(d)){
        if (!(colname %in% names(data))){
          data[,colname] = NA
        }
      }
      for(colname in names(data)){
        if(!(colname %in% names(d))){
          d[,colname]=NA
        }
      }
      # print('about to rbind')
      data = rbind(data,d)
    }
  }
  
  data$modelrun_ID = as.factor(data$modelrun_ID)
  data$agent_type = as.factor(data$agent_type)
  data$game_name = as.factor(as.character(lapply(as.vector(data$game_name), remove_string_from_name)))
  if (data_to_load=='EMPA'){
    data$episode_number = as.character(data$episode_number)
    data$event_type=as.factor(data$event_type)
  }else if (data_to_load=='human'){
    data$episode_number = as.character(data$episode_number)
    data$event_type=as.factor(data$event_type)
  }else if (data_to_load=='DDQN'){
    data$episode_number = as.character(data$episode_number)
    data$event_type=as.factor(data$event_name)
    data$level_number = as.factor(data$game_level)
    data = select(data, -event_name, -game_level)
  }
  data$short_agent_type = NA
  if (data_to_load =='human'){
    data$short_agent_type = as.factor(data_to_load)
  }else if (data_to_load == 'DDQN'){
    data$short_agent_type = data$agent_type
  }else if (data_to_load == 'EMPA'){
    e_greedy_05='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_sTE=1000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
    e_greedy_1a='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_fe=0.1_sTE=1000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
    e_greedy_1b='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_fe=0.1_sTE=2000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
    
    if (e_greedy_1a %in% unique(data$agent_type)){
      data[data$agent_type==e_greedy_1a,]$short_agent_type = 'e-greedy .1'
    }
    if (e_greedy_1b %in% unique(data$agent_type)){
      data[data$agent_type==e_greedy_1b,]$short_agent_type = 'e-greedy .1'
    }
    if (e_greedy_05 %in% unique(data$agent_type)){
      data[data$agent_type==e_greedy_05,]$short_agent_type = 'e-greedy .05'
    }
    for (agent in unique(data$agent_type)){
      if (grepl('rand=True', agent)){
        data[grepl('rand=True', data$agent_type),]$short_agent_type = 'random policy'
      }
    }
    if (NA %in% unique(data$short_agent_type)){
      data[is.na(data$short_agent_type),]$short_agent_type = 'EMPA'
    }
    
  }
  data = select(data, -agent_type) ## remove agent_type. too long.
  # sort the names into a canonical order.
  data = data[,c("subject_ID", "modelrun_ID", "game_name", "level_number", "event_type", "count","short_agent_type")]
  # add zero-count interactions. NOTE: this may take a long time if you're going through a lot of data. Should be optimized.
  data = add_zero_count_interactions(interactiondata=data)
  return (data)
}

### Find all the interaction names that could exist for each game (that include the avatar),
### and add 0-count interactions for each subject-episode_number combination that doesn't contain them.
add_zero_count_interactions = function(interactiondata){
  outputframe = interactiondata
  for (game in unique(interactiondata$game_name)){
    game_subset = filter(interactiondata, game_name==game)
    episode_numbers = unique(game_subset$episode_number)
    all_event_types = unique(game_subset$event_type)
    avatar_event_types = all_event_types[grepl('avatar', all_event_types)]
    for (subject in unique(game_subset$subject_ID)){
      agent_data = filter(game_subset, subject_ID==subject)
      agent_type = unique(agent_data$agent_type)[1]
      modelrun_ID = unique(agent_data$modelrun_ID)[1]
      short_agent_type = unique(agent_data$short_agent_type)[1]
      for (episode in episode_numbers){
        subject_episode_combo = filter(game_subset, subject_ID==subject, episode_number==episode)
        ### if this has length 0 then you need to go through all the episode numbers and add rows.
        for (event_type in avatar_event_types){
          if (!(event_type %in% unique(subject_episode_combo$event_type))){
            row = data.frame(agent_type = agent_type, 
                             subject_ID=subject, 
                             modelrun_ID = modelrun_ID, 
                             game_name = game,
                             level_number = NA, 
                             event_type = event_type, 
                             count = 0, 
                             episode_number = episode, 
                             short_agent_type = short_agent_type,
                             game_level=NA)
            outputframe = rbind(outputframe, row)
          }
        }
      }
    }
  }
  return(outputframe)
}


add_valence_to_data = function(interactiondata){
  outdata = data.frame(subject_ID=as.character(), modelrun_ID=as.character(), game_name=as.character(), 
                       level_number=as.numeric(), event_type=as.character(), count=as.numeric(), short_agent_type=as.character(), valence=as.character())
  for (game in unique(interactiondata$game_name)){
    data = filter(interactiondata, game_name==game)
    if (grepl('aliens', game)){
      data$valence = ifelse(grepl('alien', data$event_type), 'negative',
                            ifelse(grepl('bomb', data$event_type), 'negative',
                                   ifelse(grepl('sam', data$event_type), 'instrumental',
                                          'neutral')))
    }else if (grepl('avoidgeorge', game)){
      data$valence = ifelse(grepl('george', data$event_type), 'negative',
                            'neutral')
    }else if (grepl('bait', game)){
      data$valence = ifelse(grepl('hole', data$event_type), 'negative',
                            ifelse(grepl('box', data$event_type), 'instrumental',
                                   ifelse(grepl('leftPistol', data$event_type), 'instrumental',
                                          ifelse(grepl('downPistol', data$event_type), 'instrumental',
                                                 ifelse(grepl('mold', data$event_type), 'instrumental',
                                                        ifelse(grepl('key', data$event_type), 'positive',
                                                               ifelse(grepl('mushroom', data$event_type), 'positive',
                                                                      ifelse(grepl('goal', data$event_type), 'positive',
                                                                             'neutral'))))))))
    }else if (grepl('bees_and_birds', game)){
      data$valence = ifelse(grepl('bee', data$event_type), 'negative',
                            ifelse(grepl('obstacle', data$event_type), 'negative',
                                   ifelse(grepl('fence', data$event_type), 'instrumental',
                                          ifelse(grepl('goal', data$event_type), 'positive',
                                                 'neutral'))))
    }else if (grepl('boulderdash', game)){
      print ('got to boulderdash')
      data$valence = ifelse(grepl('butterfly', data$event_type), 'negative',
                            ifelse(grepl('crab', data$event_type), 'negative',
                                   ifelse(grepl('dirt', data$event_type), 'instrumental',
                                          ifelse(grepl('diamond', data$event_type), 'positive',
                                                 ifelse(grepl('exitdoor', data$event_type), 'positive',
                                                        'neutral')))))
    }else if (game == 'butterflies'){
      data$valence = ifelse(grepl('butterfly', data$event_type), 'positive',
                            'neutral')
    }else if (grepl('butterflies_1', game)){
      data$valence = ifelse(grepl('butterfly', data$event_type), 'positive',
                            'neutral')
    }else if (grepl('butterflies_2', game)){
      data$valence = ifelse(grepl('butterfly', data$event_type), 'positive',
                            'neutral')
    }else if (game %in% c('chase', 'chase_1')){
      data$valence = ifelse(grepl('angry', data$event_type), 'negative',
                            ifelse(grepl('scared', data$event_type), 'positive',
                                   'neutral'))
    }else if (game %in% c('chase_2', 'chase_3')){
      data$valence = ifelse(grepl('angry', data$event_type), 'negative',
                            ifelse(grepl('wolf', data$event_type), 'negative',
                                   ifelse(grepl('missile1', data$event_type), 'positive',
                                          ifelse(grepl('missile2', data$event_type), 'positive',
                                                 ifelse(grepl('scared', data$event_type), 'positive',
                                                        'neutral')))))
    }else if (game %in% c('closing_gates')){
      data$valence = ifelse(grepl('goal', data$event_type), 'positive',
                            'neutral')
    }else if (game %in% ('closing_gates_1')){
      data$valence = ifelse(grepl('goal', data$event_type), 'positive',
                            ifelse(grepl('boulder', data$event_type), 'instrumental',
                                   'neutral'))
    }
    else if (grepl('corridor', game)){
      data$valence = ifelse(grepl('fastL', data$event_type), 'negative',
                            ifelse(grepl('mediumL', data$event_type), 'negative',
                                   ifelse(grepl('slowL', data$event_type), 'negative',
                                          ifelse(grepl('fastR', data$event_type), 'negative',
                                                 ifelse(grepl('mediumR', data$event_type), 'negative',
                                                        ifelse(grepl('slowR', data$event_type), 'negative',
                                                               ifelse(grepl('goal', data$event_type), 'positive',
                                                                      'neutral')))))))
    }else if (game %in% c('antagonist', 'antagonist_1', 'antagonist_2')){
      data$valence = ifelse(grepl('box1', data$event_type), 'positive',
                            ifelse(grepl('box2', data$event_type), 'instrumental',
                                   ifelse(grepl('box3', data$event_type), 'instrumental',
                                          ifelse(grepl('forcefield', data$event_type), 'instrumental',
                                                 'neutral'))))
    }else if (game %in% c('ee', 'ee_1', 'ee_2')){
      data$valence = ifelse(grepl('chaser', data$event_type), 'negative',
                            ifelse(grepl('apple', data$event_type), 'positive',
                                   ifelse(grepl('blueberry', data$event_type), 'positive',
                                          ifelse(grepl('orange', data$event_type), 'positive',
                                                 ifelse(grepl('dough', data$event_type), 'positive',
                                                        ifelse(grepl('eel', data$event_type), 'positive',
                                                               ifelse(grepl('fruit', data$event_type), 'positive',
                                                                      'neutral'))))))) 
    }else if (game == 'ee_3'){
      data$valence = ifelse(grepl('cranberry', data$event_type), 'negative',
                            ifelse(grepl('apple', data$event_type), 'positive',
                                   ifelse(grepl('blueberry', data$event_type), 'positive',
                                          ifelse(grepl('orange', data$event_type), 'positive',
                                                 ifelse(grepl('dough', data$event_type), 'positive',
                                                        ifelse(grepl('eel', data$event_type), 'positive',
                                                               ifelse(grepl('fruit', data$event_type), 'positive',
                                                                      'neutral'))))))) 
    }else if (grepl('frogs', game)){
      data$valence = ifelse(grepl('water', data$event_type), 'negative',
                            ifelse(grepl('slowRtruck', data$event_type), 'negative',
                                   ifelse(grepl('fastRtruck', data$event_type), 'negative',
                                          ifelse(grepl('slowLtruck', data$event_type), 'negative',
                                                 ifelse(grepl('fastLtruck', data$event_type), 'negative',
                                                        ifelse(grepl('log', data$event_type), 'instrumental',
                                                               ifelse(grepl('entry', data$event_type), 'instrumental',
                                                                      ifelse(grepl('exit1', data$event_type), 'instrumental',
                                                                             ifelse(grepl('bridge', data$event_type), 'instrumental',
                                                                                    ifelse(grepl('goal', data$event_type), 'positive',
                                                                                           'neutral'))))))))))
    }else if (grepl('lemmings', game)){
      data$valence = ifelse(grepl('hole', data$event_type), 'negative',
                            ifelse(grepl('snake', data$event_type), 'negative',
                                   ifelse(grepl('mole', data$event_type), 'negative',
                                          'neutral')))
    }else if (game == 'missilecommand_2'){
      data$valence = ifelse(grepl('explosion', data$event_type), 'negative',
                            'neutral')
    }else if (game == 'missilecommand_3'){
      data$valence = ifelse(grepl('incoming_slow', data$event_type), 'negative',
                            ifelse(grepl('incoming_fast', data$event_type), 'negative',
                                   'neutral'))
    }else if (grepl('myAliens', game)){
      data$valence = ifelse(grepl('ghost', data$event_type), 'negative',
                            ifelse(grepl('gate', data$event_type), 'positive',
                                   ifelse(grepl('alien', data$event_type), 'positive',
                                          'neutral')))
    }else if (grepl('plaqueattack', game)){
      data$valence = ifelse(grepl('deadMolarInf', data$event_type), 'positive',
                            ifelse(grepl('deadMolarSup', data$event_type), 'positive',
                                   ifelse(grepl('adversary', data$event_type), 'negative',
                                          ifelse(grepl('laser', data$event_type), 'negative',
                                                 'neutral'))))
    }else if(grepl('portals', game)){
      data$valence = ifelse(grepl('sitting', data$event_type), 'negative',
                            ifelse(grepl('random', data$event_type), 'negative',
                                   ifelse(grepl('chaser', data$event_type), 'negative',
                                          ifelse(grepl('vertical', data$event_type), 'negative',
                                                 ifelse(grepl('horizontal', data$event_type), 'negative',
                                                        ifelse(grepl('entry1', data$event_type), 'instrumental',
                                                               ifelse(grepl('entry2', data$event_type), 'instrumental',
                                                                      ifelse(grepl('entry3', data$event_type), 'instrumental',
                                                                             ifelse(grepl('exit1', data$event_type), 'instrumental',
                                                                                    ifelse(grepl('exit2', data$event_type), 'instrumental',
                                                                                           ifelse(grepl('exit3', data$event_type), 'instrumental',
                                                                                                  ifelse(grepl('goal', data$event_type), 'positive',
                                                                                                         'neutral'))))))))))))
    }else if (grepl('preconditions', game)){
      data$valence = ifelse(grepl('goal', data$event_type), 'positive',
                            ifelse(grepl('medicine', data$event_type), 'instrumental',
                                   ifelse(grepl('poison', data$event_type), 'negative',
                                          'neutral')))
    }else if (game %in% c('push_boulders', 'push_boulders_1')){
      data$valence = ifelse(grepl('poison1', data$event_type), 'negative',
                            ifelse(grepl('poison2', data$event_type), 'negative',
                                   ifelse(grepl('poison3', data$event_type), 'negative',
                                          ifelse(grepl('box1', data$event_type), 'instrumental',
                                                 ifelse(grepl('dynamite', data$event_type), 'instrumental',
                                                        ifelse(grepl('goal', data$event_type), 'positive',
                                                               'neutral'))))))
    }else if (game %in% c('push_boulders_2')){
      data$valence = ifelse(grepl('poison1', data$event_type), 'negative',
                            ifelse(grepl('poison2', data$event_type), 'negative',
                                   ifelse(grepl('poison3', data$event_type), 'negative',
                                          ifelse(grepl('box1', data$event_type), 'instrumental',
                                                 ifelse(grepl('fuseright', data$event_type), 'instrumental',
                                                        ifelse(grepl('fuseup', data$event_type), 'instrumental',
                                                               ifelse(grepl('litfuseright', data$event_type), 'instrumental',
                                                                      ifelse(grepl('litfuseup', data$event_type), 'instrumental',
                                                                             ifelse(grepl('goal', data$event_type), 'positive',
                                                                                    'neutral')))))))))
    }else if (game=='relational'){
      data$valence = ifelse(grepl('probe', data$event_type), 'instrumental',
                            ifelse(grepl('converter1', data$event_type), 'instrumental',
                                   ifelse(grepl('fire', data$event_type), 'instrumental',
                                          ifelse(grepl('box1', data$event_type), 'instrumental',
                                                 ifelse(grepl('converter3', data$event_type), 'instrumental',
                                                        'neutral')))))
    }else if (game%in%c('relational_1', 'relational_2')){
      data$valence = ifelse(grepl('converter1', data$event_type), 'instrumental',
                            ifelse(grepl('box1', data$event_type), 'instrumental',
                                   ifelse(grepl('converter3', data$event_type), 'instrumental',
                                          'neutral')))
    }else if (grepl('sokoban', game)){
      data$valence = ifelse(grepl('box', data$event_type), 'instrumental',
                            ifelse(grepl('hole', data$event_type), 'instrumental',
                                   ifelse(grepl('fence', data$event_type), 'instrumental',
                                          ifelse(grepl('portal1', data$event_type), 'instrumental',
                                                 'neutral'))))
    }else if (game=='surprise'){
      data$valence = ifelse(grepl('apple', data$event_type), 'positive',
                            'neutral')
    }else if (game=='surprise_1'){
      data$valence = ifelse(grepl('apple', data$event_type), 'positive',
                            ifelse(grepl('inert', data$event_type), 'negative',
                                   'neutral'))
    }else if (game=='surprise_2'){
      data$valence = ifelse(grepl('inert', data$event_type), 'positive',
                            'neutral')
    }else if (game%in%c('survivezombies','survivezombies_1')){
      data$valence = ifelse(grepl('honey', data$event_type), 'positive',
                            ifelse(grepl('slowHell', data$event_type), 'negative',
                                   ifelse(grepl('fastHell', data$event_type), 'negative',
                                          ifelse(grepl('zombie', data$event_type), 'negative',
                                                 'neutral'))))
    }else if (game=='survivezombies_2'){
      data$valence = ifelse(grepl('honey', data$event_type), 'positive',
                            ifelse(grepl('slowHell', data$event_type), 'negative',
                                   ifelse(grepl('fastHell', data$event_type), 'negative',
                                          ifelse(grepl('zombie', data$event_type), 'positive',
                                                 'neutral'))))
    }else if (grepl('watergame', game)){
      data$valence = ifelse(grepl('door', data$event_type), 'positive',
                            ifelse(grepl('box', data$event_type), 'instrumental',
                                   ifelse(grepl('antibox', data$event_type), 'instrumental',
                                          ifelse(grepl('part1', data$event_type), 'instrumental',
                                                 ifelse(grepl('part2', data$event_type), 'instrumental',
                                                        ifelse(grepl('water', data$event_type), 'negative',
                                                               ifelse(grepl('fastHell', data$event_type), 'negative',
                                                                      'neutral')))))))
    }else if (grepl('zelda', game)){
      data$valence = ifelse(grepl('monsterQuick', data$event_type), 'negative',
                            ifelse(grepl('monsterNormal', data$event_type), 'negative',
                                   ifelse(grepl('monsterSlow', data$event_type), 'negative',
                                          ifelse(grepl('key', data$event_type), 'instrumental',
                                                 ifelse(grepl('goal', data$event_type), 'positive',
                                                        'neutral')))))
    }else{
      data$valence = NA
      ## omitting jaws (bc shark interactions are good/bad depending on what avatar is carrying)
      ## omitting missilecommand 0 1 4 because there are no direct avatar interactions that are good/bad
      ## omitting helper
    }
    outdata = rbind(outdata, data)
  }
  return(outdata)
}

make_sum_dataframes = function(data){
  sum_dataframe = data.frame(short_agent_type=as.character(), game_name=as.character(), level=as.numeric(), valence=as.character(), raw_count=as.numeric(),
                             across_level_normalized_count=as.numeric(), per_level_normalized_count=as.numeric())
  for (game in unique(data$game_name)){
    game_data = filter(data, game_name==game)
    sum_data = make_sum_dataframe(game_data, game)
    sum_dataframe = rbind(sum_dataframe, sum_data)
  }
  return(sum_dataframe)
}

cross_entropy = function(p, q, constant){
  p = as.numeric(p)
  q = as.numeric(q)
  p = p+constant
  q = q+constant
  p = p/sum(p)
  q = q/sum(q)
  # if (0 %in% p){
  #   p = p+0.01
  #   p = p/sum(p)
  # }
  # if (0 %in% q){
  #   q = q+0.01
  #   q = q/sum(q)
  # }
  s = 0
  for (i in 1:length(p)){
    s = s - p[i]*log(q[i], 2)
  }
  return (s)
}
make_sum_dataframe = function(data, game_name){
  sum_data = data.frame(short_agent_type=as.character(), game_name=as.character(), level=as.numeric(), valence=as.character(), raw_count=as.numeric(),
                        across_level_normalized_count=as.numeric(), per_level_normalized_count=as.numeric(),
                        across_level_no_neutral_normalized_count=as.numeric(), per_level_no_neutral_normalized_count=as.numeric())
  for (agent in unique(data$short_agent_type)){
    agent_data = filter(data, short_agent_type==agent, grepl('avatar', event_type))
    z = sum(agent_data$count)
    z_no_neutral = sum(filter(agent_data, valence!='neutral')$count)
    for (vlc in c('positive','instrumental','neutral', 'negative')){
      across_level_cnt = sum(filter(agent_data, valence==vlc)$count)
      if(vlc=='neutral'){
        across_level_no_neutral_cnt = NA
      }else{
        across_level_no_neutral_cnt = across_level_cnt
      }
      for (level in unique(agent_data$level)){
        agent_level_data = filter(agent_data, level_number==level)
        agent_level_no_neutral_data = filter(agent_data, level_number==level, valence!='neutral')
        z_1 = sum(agent_level_data$count)
        z_2 = sum(agent_level_no_neutral_data$count)
        per_level_cnt = sum(filter(agent_level_data, valence==vlc)$count)
        if(vlc=='neutral'){
          per_level_cnt_for_no_neutral = NA
        }else{
          per_level_cnt_for_no_neutral = per_level_cnt
        }
        row = data.frame(short_agent_type=agent, game_name=game_name, level=level, valence=vlc, raw_count=per_level_cnt,
                         across_level_normalized_count=across_level_cnt/z, per_level_normalized_count=per_level_cnt/z_1, 
                         across_level_no_neutral_normalized_count=across_level_no_neutral_cnt/z_no_neutral,
                         per_level_no_neutral_normalized_count=per_level_cnt_for_no_neutral/z_2)
        sum_data = rbind(sum_data, row)
      }    
    }
    
  }
  return(sum_data)
}


calculate_distance = function(v1,v2,metric,constant){
  ## constant is only used for cross-entropy
  v1=as.numeric(v1)
  v2=as.numeric(v2)
  
  if (missing(constant)){
    constant = ''
  }
  
  if (metric=='cosine'){
    return(cosine(v1,v2))
  }
  else if (metric=='avg_absolute_difference'){
    return(mean(abs(v1-v2)))
  }
  else if (metric=='avg_squared_difference'){
    return(mean((v1-v2)**2))
  }
  else if (metric=='cross-entropy'){
    return(cross_entropy(v1, v2, constant))
  }
}

calculate_proportion_of_games_best_fit_by_each_model = function(distance_df){
  counts=c()
  games=c()
  for (game in unique(distance_df$game_name)){
    game_data = filter(distance_df, game_name==game)
    if (!is.nan(sum(as.numeric(as.character(game_data$distance)), na.rm=TRUE)) & sum(as.numeric(as.character(game_data$distance)),na.rm=TRUE)>0){
      counts = c(counts,as.character(game_data[game_data$distance==min(as.numeric(as.character(game_data$distance))),]$type))
      games=c(games, game)
    }
  }
  counts=na.omit(counts)
  absolute_normalized_counts = data.frame(type=as.character(), normalized_count=as.numeric(), metric=as.character())
  z=length(counts)
  for (corr_type in unique(counts)){
    row = data.frame(type=corr_type, normalized_count=sum(counts==corr_type)/z, metric=distance_df$metric[1])
    absolute_normalized_counts = rbind(absolute_normalized_counts, row)
  }
  return(absolute_normalized_counts)
}

find_best_model = function(distance_df){
  best_model_df = data.frame(game_name=as.character(), best_model=as.character(), margin=as.numeric())
  for (game in unique(distance_df$game_name)){
    game_data = filter(distance_df, game_name==game)
    best = min(as.numeric(as.character(game_data$distance)))
    second_best = as.numeric(as.character(sort(game_data$distance,decreasing=FALSE)[2]))
    margin = second_best - best
    row = game_data[as.numeric(as.character(game_data$distance))==best,][c('game_name', 'type', 'metric')]
    row$margin = margin
    best_model_df = rbind(best_model_df, row)
  }
  return(best_model_df)
}

create_distance_dataframe = function(count_df, metric, constant){
  ## count_df: mean_raw_count_df: mean per-subject counts  or normalized_per_agent_counts
  ## constant is only used for cross-entropy loss
  ## Choices for metric: 'cosine', 'avg_absolute_difference', 'avg_squared_difference', 'cross-entropy'
  
  ### Calculate squared differences of absolute model counts:
  human_empa=c()
  human_random=c()
  human_e_greedy=c()
  human_ddqn=c()
  
  ## Calculate distance between models in absolute counts
  for (game in unique(count_df$game_name)){
    game_data = filter(count_df, game_name==game)
    human_empa = c(human_empa,  calculate_distance(c(filter(game_data, short_agent_type=='human', valence=='positive')$mean_count, 
                                                     filter(game_data, short_agent_type=='human', valence=='instrumental')$mean_count,
                                                     filter(game_data, short_agent_type=='human', valence=='neutral')$mean_count,
                                                     filter(game_data, short_agent_type=='human', valence=='negative')$mean_count),
                                                   c(filter(game_data, short_agent_type=='EMPA', valence=='positive')$mean_count, 
                                                     filter(game_data, short_agent_type=='EMPA', valence=='instrumental')$mean_count,
                                                     filter(game_data, short_agent_type=='EMPA', valence=='neutral')$mean_count,
                                                     filter(game_data, short_agent_type=='EMPA', valence=='negative')$mean_count),
                                                   metric, constant))
    human_random = c(human_random,  calculate_distance(c(filter(game_data, short_agent_type=='human', valence=='positive')$mean_count, 
                                                         filter(game_data, short_agent_type=='human', valence=='instrumental')$mean_count,
                                                         filter(game_data, short_agent_type=='human', valence=='neutral')$mean_count,
                                                         filter(game_data, short_agent_type=='human', valence=='negative')$mean_count),
                                                       c(filter(game_data, short_agent_type=='random policy', valence=='positive')$mean_count, 
                                                         filter(game_data, short_agent_type=='random policy', valence=='instrumental')$mean_count,
                                                         filter(game_data, short_agent_type=='random policy', valence=='neutral')$mean_count,
                                                         filter(game_data, short_agent_type=='random policy', valence=='negative')$mean_count),
                                                       metric, constant))
    human_e_greedy = c(human_e_greedy,  calculate_distance(c(filter(game_data, short_agent_type=='human', valence=='positive')$mean_count, 
                                                             filter(game_data, short_agent_type=='human', valence=='instrumental')$mean_count,
                                                             filter(game_data, short_agent_type=='human', valence=='neutral')$mean_count,
                                                             filter(game_data, short_agent_type=='human', valence=='negative')$mean_count),
                                                           c(filter(game_data, short_agent_type=='e-greedy .1', valence=='positive')$mean_count, 
                                                             filter(game_data, short_agent_type=='e-greedy .1', valence=='instrumental')$mean_count,
                                                             filter(game_data, short_agent_type=='e-greedy .1', valence=='neutral')$mean_count,
                                                             filter(game_data, short_agent_type=='e-greedy .1', valence=='negative')$mean_count),
                                                           metric, constant))
    human_ddqn = c(human_ddqn,  calculate_distance(c(filter(game_data, short_agent_type=='human', valence=='positive')$mean_count, 
                                                     filter(game_data, short_agent_type=='human', valence=='instrumental')$mean_count,
                                                     filter(game_data, short_agent_type=='human', valence=='neutral')$mean_count,
                                                     filter(game_data, short_agent_type=='human', valence=='negative')$mean_count),
                                                   c(filter(game_data, short_agent_type=='DDQN 100k', valence=='positive')$mean_count, 
                                                     filter(game_data, short_agent_type=='DDQN 100k', valence=='instrumental')$mean_count,
                                                     filter(game_data, short_agent_type=='DDQN 100k', valence=='neutral')$mean_count,
                                                     filter(game_data, short_agent_type=='DDQN 100k', valence=='negative')$mean_count),
                                                   metric, constant))
  }
  corr_frame_vert_absolute = data.frame(rbind(
    cbind(as.character(unique(count_df$game_name)), 'human_empa', human_empa),
    cbind(as.character(unique(count_df$game_name)), 'human_e_greedy', human_e_greedy),
    cbind(as.character(unique(count_df$game_name)), 'human_random', human_random),
    cbind(as.character(unique(count_df$game_name)), 'human_ddqn', human_ddqn)))
  names(corr_frame_vert_absolute) = c('game_name', 'type', 'distance')
  
  if (missing(constant)){
    constant = ''
  }
  corr_frame_vert_absolute$metric = paste(metric, as.character(constant), sep=' ')
  return(corr_frame_vert_absolute)
}

calculate_proportions = function(best_model_df, margin_cutoff){
  proportion_df = data.frame(type=as.character(), normalized_count=as.numeric(), metric=as.character())
  z=length(filter(normalized_abs_distance_best_models, margin>margin_cutoff)$margin)
  for (model in unique(best_model_df$type)){
    proportion = sum(filter(normalized_abs_distance_best_models, margin>margin_cutoff)$type==model)/z
    row = data.frame(type=model, normalized_count=proportion, metric=best_model_df$metric[1])
    proportion_df = rbind(proportion_df, row)
  }
  return(proportion_df)
}

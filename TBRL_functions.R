### Helper functions for TBRL analyses

library(here)
library(cowplot)
library("ggplot2")
library("zoom")
library("stats")
library(plyr)
library("dplyr")
library("colorspace")
library("RColorBrewer")
library(purrr)
library(zoo)
library(EnvStats)
library(grid)
library(plotrix)


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
  ## make data structure for looking at levels_won for different planner settings (corresponding to runs on different days)
  plantimedata = data.frame(game_name=as.character(), agent_type=as.character(), max_score=as.numeric(), 
                            max_steps=as.numeric(), planning_time=as.numeric(), max_levels_won=as.numeric(),
                            level_num=as.numeric(), level_efficiency=as.numeric())
  
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
        idx=1
        for (k in 1:length(unique(s$subject_ID))){
          subject = unique(s$subject_ID)[k]
          subjectdata = s[which(s$subject_ID==subject),]
          if (length(subjectdata$cumulative_steps)>0){
            if(max(subjectdata$cumulative_steps)>0){
              level_maxes[[idx]] = max(subjectdata$cumulative_wins)
              cumulative_step_maxes[[idx]] = max(subjectdata$cumulative_steps)
              idx = idx+1            
            }
            
          }
        }
        
        ## mean vector of win numbers
        mean_wins = mean(as.numeric(as.vector(level_maxes)))
        
        ##mean of vector steps+to+win ratios
        l_e = mean(as.numeric(as.vector(level_maxes))/as.numeric(as.vector(cumulative_step_maxes)))
        
        ## the row we want
        r = subset(s, cumulative_steps==max(cumulative_steps))[1,]
        ## take only the relevant columns and put them in the new data frame
        new = data.frame(game_name=r$game_name, agent_type=r$agent_type, max_score=r$score, 
                         max_steps=r$cumulative_steps, mean_levels_won=mean_wins,
                         level_num=subset(games_to_levels, (game_name==r$game_name))$num_levels,
                         level_efficiency=l_e)
        plantimedata = rbind(plantimedata, new)
      }
    }
  }
  
  
  plantimedata = mutate(plantimedata, level_percentage=mean_levels_won/level_num)
  plantimedata = mutate(plantimedata, composite_ratio = level_percentage*level_efficiency)
  
  plantimedata$human_normed_composite_ratio=NA
  ##norm by human level_efficiency
  for (i in 1:length(unique(plantimedata$game_name))){
    game = unique(plantimedata$game_name)[i]
    human_composite_ratio = subset(plantimedata, agent_type=='human' & game_name==game)$composite_ratio
    for (agent in unique(plantimedata$agent_type)){
      row = plantimedata[which(plantimedata$agent_type==agent & plantimedata$game_name==game),]
      plantimedata[which(plantimedata$agent_type==agent & plantimedata$game_name==game),]$human_normed_composite_ratio = row$composite_ratio/human_composite_ratio
    }
  }
  
  for (i in 1:length(plantimedata$human_normed_composite_ratio)){
    if (plantimedata$human_normed_composite_ratio[i]==0){
      plantimedata$human_normed_composite_ratio[i]=10e-8
    }
  }
  return(plantimedata)
}

load_reward_data = function(data_to_load, dates_or_groups){
  if (data_to_load=='EMPA'){
    data = c()
    for (date in dates_or_groups){
      path = paste(getwd(),'/data_files/EMPA/', date,'/csv_data/merged_data',sep='')
      # path = paste('~/Projects/atari/vgdl_data_files/',date, '/csv_data/merged_data', sep='')
      d=read.csv(path, header=TRUE, na.strings='NA')
      
      # if ('exploration_burn_ins' %in% names(d)){
      #   d$exploration_burn_ins = as.numeric(d$exploration_burn_ins) ## you might want to make this as.numeric()
      # }else{
      #   d$exploration_burn_ins = NA
      # }
      
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
    
    
    ### e-greedy ones are poorly named?
    ## You ran 2k N on apr 4
    ## and you have 2k DS here
    
    ##
    
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
                  -episode_end, -win, -planner_nodes, -planner_settings, -cumulative_planner_nodes, 
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
    data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score')]
  }else if (data_to_load == 'DDQN'){
    dqndata = list()
    for (gamefile in list.files(dqn_path)){
      filename = paste(dqn_path,gamefile,sep='')
      if(grepl('dqn/', filename)){
        gamenamestart = unlist(gregexpr('dqn/',filename))+nchar('dqn/')
        gamenameend = unlist(gregexpr('_reward', filename))+1        
      }else if (grepl('dqn_data/', filename)){
        gamenamestart = unlist(gregexpr('dqn_data/',filename))+nchar('dqn_data/')
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
    data = select(data, -criteria, -level, -ep_reward)
    data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score')]
    
  }else if (data_to_load == 'rainbow'){
    rainbowdata = list()
    for (gamefile in list.files(rainbow_path)){
      filename = paste(rainbow_path,gamefile,sep='')
      if(grepl('rainbow/', filename)){
        gamenamestart = unlist(gregexpr('rainbow/',filename))+nchar('rainbow/')
        gamenameend = unlist(gregexpr('_reward', filename))+1        
      }else if (grepl('rainbowdata/', filename)){
        gamenamestart = unlist(gregexpr('rainbowdata/',filename))+nchar('rainbowdata/')
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
      
      ## WARNING: This is not robust to ordering trial numbers differently.
      if (grepl('trial10', filename)){
        d$agent_type = as.factor("rainbow 50k") ## refers to the eps_decay (epsilon-greedy annealing) parameter in the DDQN implementation.
      }else if (grepl('trial1', filename)){
        d$agent_type = as.factor("rainbow 250k")
      }else if (grepl('trial23', filename)){
        d$agent_type = as.factor("rainbow 150k")
      }else{
        d$agent_type = as.factor("rainbow")
      }
      
      
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
    data = select(data, -criteria, -level, -ep_reward)
    data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score')]
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
    data = select(data, -criteria, -level, -ep_reward)
    data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score')]
  }
  else if (data_to_load == 'human'){
    humandata = list()
    for (humandatapath in humandatapaths){
      path = paste('~/Projects/atari/vgdl/vgdl/humandata/',humandatapath, sep='')
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
    data = humandata
    data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score')]
  }
  
  data$game_name = as.factor(as.character(lapply(as.vector(data$game_name), remove_string_from_name)))
  # beep(sound=2)
  return (data)
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